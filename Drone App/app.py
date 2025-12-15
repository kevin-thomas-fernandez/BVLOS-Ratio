import os
import json
import numpy as np
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from typing import List, Dict
import re
import random
from collections import Counter

app = Flask(__name__)

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyBEZYhCh_Xp-d4ztL_0vTUIpuoSU-3TuoQ')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Pre-defined synonym dictionary for fast lookup (no external dependencies)
SYNONYM_DICT = {
    'weight': ['mass', 'pound', 'lb', 'lbs', 'weight limit', 'maximum weight', 'weight restriction', 
               'weight requirement', 'weight capacity', 'pound limit', 'mass limit'],
    'speed': ['velocity', 'mph', 'knots', 'knot', 'speed limit', 'maximum speed', 'speed restriction',
              'velocity limit', 'mph limit', 'airspeed'],
    'altitude': ['height', 'feet', 'ft', 'AGL', 'altitude limit', 'maximum altitude', 'height limit',
                 'ceiling', 'AGL limit', 'above ground level'],
    'drone': ['UAS', 'UA', 'unmanned aircraft', 'unmanned aircraft system', 'quadcopter', 'multirotor'],
    'limit': ['maximum', 'restriction', 'requirement', 'cap', 'ceiling', 'threshold'],
    'permit': ['certificate', 'license', 'authorization', 'approval', 'clearance'],
    'operation': ['flight', 'mission', 'operation', 'flying', 'piloting'],
    'distance': ['range', 'radius', 'proximity', 'separation', 'away'],
    'safety': ['security', 'protection', 'precaution', 'safeguard'],
    'regulation': ['rule', 'law', 'requirement', 'standard', 'guideline'],
    'beyond': ['BVLOS', 'beyond visual line of sight', 'out of sight'],
    'visual': ['sight', 'view', 'line of sight', 'LOS', 'VLOS'],
}

# Simple TF-IDF like embeddings without heavy dependencies
def create_simple_embedding(text):
    """Create a simple embedding using word frequency (lightweight alternative)"""
    words = re.findall(r'\w+', text.lower())
    # Create a simple vector representation
    word_counts = Counter(words)
    return word_counts

class FastRetriever:
    """Fast inverted index-based retriever with synonym support"""
    def __init__(self, rules, synonym_dict):
        self.rules = rules
        self.synonym_dict = synonym_dict
        self.inverted_index = {}
        self.build_index()
    
    def build_index(self):
        """Build inverted index: word -> [rule_ids] for O(1) lookup"""
        print("Building inverted index...")
        for idx, rule in enumerate(self.rules):
            text = f"{rule.get('title', '')} {rule.get('description', '')} {rule.get('definition', '')}"
            words = set(re.findall(r'\w+', text.lower()))
            
            # Add word and all its synonyms to index
            for word in words:
                if word not in self.inverted_index:
                    self.inverted_index[word] = []
                if idx not in self.inverted_index[word]:
                    self.inverted_index[word].append(idx)
                
                # Add synonyms
                if word in self.synonym_dict:
                    for syn in self.synonym_dict[word]:
                        syn_normalized = syn.lower().replace(' ', '_')
                        if syn_normalized not in self.inverted_index:
                            self.inverted_index[syn_normalized] = []
                        if idx not in self.inverted_index[syn_normalized]:
                            self.inverted_index[syn_normalized].append(idx)
        
        print(f"Built inverted index with {len(self.inverted_index)} unique terms")
    
    def search(self, query, top_k=5):
        """Fast search using inverted index"""
        query_words = set(re.findall(r'\w+', query.lower()))
        
        # Find rules containing any query word or synonym
        rule_matches = Counter()
        for word in query_words:
            # Direct match
            if word in self.inverted_index:
                for rule_id in self.inverted_index[word]:
                    rule_matches[rule_id] += 1
            
            # Synonym match
            if word in self.synonym_dict:
                for syn in self.synonym_dict[word]:
                    syn_normalized = syn.lower().replace(' ', '_')
                    if syn_normalized in self.inverted_index:
                        for rule_id in self.inverted_index[syn_normalized]:
                            rule_matches[rule_id] += 1
        
        # Return top-k by match count
        sorted_rules = sorted(rule_matches.items(), key=lambda x: x[1], reverse=True)
        return [self.rules[rule_id] for rule_id, _ in sorted_rules[:top_k]]


class DroneRAG:
    def __init__(self, rules_file='parsed_rules.json'):
        """Initialize the RAG system with drone rules"""
        self.rules = []
        self.embeddings = []
        self.synonym_dict = SYNONYM_DICT
        self.fast_retriever = None
        self.knowledge_base = None  # Will store extracted terms and concepts
        self.load_rules(rules_file)
        self.create_embeddings()
        self.build_fast_retriever()
        self.build_knowledge_base()
        
    def load_rules(self, rules_file):
        """Load drone rules from JSON file"""
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                self.rules = json.load(f)
            print(f"Loaded {len(self.rules)} drone rules")
        except Exception as e:
            print(f"Error loading rules: {e}")
            self.rules = []
    
    def build_fast_retriever(self):
        """Build fast inverted index retriever"""
        if self.rules:
            self.fast_retriever = FastRetriever(self.rules, self.synonym_dict)
    
    def build_knowledge_base(self):
        """Extract all key terms, concepts, and entities from rules to build comprehensive knowledge base"""
        if not self.rules:
            return
        
        print("Building knowledge base from rules...")
        
        # Extract key terms
        all_text = ' '.join([
            f"{rule.get('title', '')} {rule.get('description', '')} {rule.get('definition', '')}"
            for rule in self.rules
        ])
        
        # Extract important terms (nouns, technical terms, numbers)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        word_freq = Counter(words)
        
        # Filter out common words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        important_words = {word: count for word, count in word_freq.items() 
                          if word not in stop_words and count >= 2 and len(word) >= 4}
        
        # Extract rule numbers
        rule_numbers = [rule.get('rule_number', '') for rule in self.rules if rule.get('rule_number')]
        
        # Extract categories
        categories = list(set([rule.get('category', '') for rule in self.rules if rule.get('category')]))
        
        # Extract operation types
        operation_types = []
        for rule in self.rules:
            desc = rule.get('description', '').lower()
            if 'package delivery' in desc:
                operation_types.append('package delivery')
            if 'agricultural' in desc or 'agriculture' in desc:
                operation_types.append('agricultural')
            if 'aerial surveying' in desc or 'surveying' in desc:
                operation_types.append('aerial surveying')
            if 'civic interest' in desc:
                operation_types.append('civic interest')
            if 'recreational' in desc:
                operation_types.append('recreational')
            if 'demonstration' in desc:
                operation_types.append('demonstration')
            if 'flight test' in desc:
                operation_types.append('flight test')
        
        operation_types = list(set(operation_types))
        
        # Extract numerical values (weights, speeds, altitudes, distances)
        numbers = re.findall(r'\b(\d{1,4}(?:,\d{3})*)\s*(pounds?|lbs?|feet?|ft|mph|knots?|miles?|nautical|hours?|days?|months?|years?)\b', all_text, re.IGNORECASE)
        numerical_values = list(set([f"{num[0]} {num[1]}" for num in numbers]))
        
        # Extract key concepts (phrases)
        key_phrases = []
        phrase_patterns = [
            r'operating (?:permit|certificate)',
            r'airworthiness acceptance',
            r'flight coordinator',
            r'operations supervisor',
            r'strategic deconfliction',
            r'conformance monitoring',
            r'detect and avoid',
            r'remote identification',
            r'population density',
            r'category \d+',
            r'BVLOS',
            r'beyond visual line of sight',
            r'ground control station',
            r'command and control',
            r'hazardous materials?',
            r'safety management',
            r'emergency procedures?',
            r'preflight requirements?',
            r'operating restrictions?',
        ]
        
        for pattern in phrase_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            key_phrases.extend(matches)
        
        key_phrases = list(set([p.lower() for p in key_phrases]))
        
        self.knowledge_base = {
            'important_words': list(important_words.keys())[:200],  # Top 200 words
            'rule_numbers': rule_numbers,
            'categories': categories,
            'operation_types': operation_types,
            'numerical_values': numerical_values[:50],  # Top 50 numerical values
            'key_phrases': key_phrases,
        }
        
        print(f"Knowledge base built: {len(important_words)} words, {len(rule_numbers)} rules, "
              f"{len(categories)} categories, {len(operation_types)} operation types, "
              f"{len(numerical_values)} numerical values, {len(key_phrases)} key phrases")
    
    def create_embeddings(self):
        """Create embeddings for all rules using simple word frequency"""
        if not self.rules:
            return
        
        print("Creating embeddings for drone rules...")
        self.embeddings = []
        for rule in self.rules:
            text = f"""
            Rule {rule.get('rule_number', '')}: {rule.get('title', '')}
            Category: {rule.get('category', '')}
            Definition: {rule.get('definition', '')}
            Description: {rule.get('description', '')}
            """
            embedding = create_simple_embedding(text)
            self.embeddings.append(embedding)
        
        print(f"Created {len(self.embeddings)} embeddings")
    
    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two word frequency vectors"""
        # Get all unique words
        all_words = set(vec1.keys()) | set(vec2.keys())
        
        if not all_words:
            return 0.0
        
        # Convert to vectors
        v1 = np.array([vec1.get(word, 0) for word in all_words])
        v2 = np.array([vec2.get(word, 0) for word in all_words])
        
        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def is_greeting(self, query: str) -> bool:
        """Detect if query is a greeting"""
        greetings = ['hi', 'hey', 'hello', 'good morning', 'good afternoon', 
                     'good evening', 'greetings', 'howdy', 'sup', 'what\'s up',
                     'how are you', 'how do you do']
        query_lower = query.lower().strip()
        return query_lower in greetings or any(query_lower.startswith(g) for g in greetings)
    
    def handle_greeting(self) -> str:
        """Generate greeting response"""
        return """Hello! 👋 I'm your FAA drone regulation assistant. I can help you with questions about Part 108 BVLOS (Beyond Visual Line of Sight) operations, including:

• **Weight and size restrictions**
• **Speed and altitude limits**  
• **Permit and certificate requirements**
• **Safety regulations and compliance**
• **Operational requirements**
• And much more!

What would you like to know about drone regulations?"""
    
    def find_relevant_rules(self, query: str, top_k: int = 5) -> List[Dict]:
        """Find most relevant rules using fast inverted index + semantic similarity"""
        if not self.embeddings:
            return []
        
        # Use fast inverted index first (with synonyms)
        if self.fast_retriever:
            fast_results = self.fast_retriever.search(query, top_k=top_k * 2)
            if fast_results:
                # Score by semantic similarity too
        query_embedding = create_simple_embedding(query)
                scored_results = []
                for rule in fast_results:
                    rule_idx = self.rules.index(rule)
                    rule_embedding = self.embeddings[rule_idx]
                    semantic_score = self._cosine_similarity(query_embedding, rule_embedding)
                    rule_copy = rule.copy()
                    rule_copy['similarity_score'] = float(semantic_score)
                    scored_results.append(rule_copy)
                
                # Sort by semantic score and return top-k
                scored_results.sort(key=lambda x: x['similarity_score'], reverse=True)
                return scored_results[:top_k]
        
        # Fallback to original semantic search
        query_embedding = create_simple_embedding(query)
        similarities = []
        for rule_embedding in self.embeddings:
            score = self._cosine_similarity(query_embedding, rule_embedding)
            similarities.append(score)
        
        similarities = np.array(similarities)
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        relevant_rules = []
        for idx in top_indices:
            rule = self.rules[idx].copy()
            rule['similarity_score'] = float(similarities[idx])
            relevant_rules.append(rule)
        
        return relevant_rules
    
    def generate_followups(self, query: str, relevant_rules: List[Dict]) -> List[str]:
        """Generate comprehensive follow-up questions using knowledge base and query context"""
        if not self.knowledge_base:
            return self._default_followups()
        
        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        
        # Extract context from relevant rules
        rule_texts = ' '.join([
            f"{r.get('title', '')} {r.get('description', '')}"
            for r in relevant_rules[:5]
        ]).lower()
        
        rule_words = set(re.findall(r'\b\w+\b', rule_texts))
        
        # Find most common categories
        categories = Counter([r.get('category', 'unknown') for r in relevant_rules])
        top_categories = [cat for cat, _ in categories.most_common(3)]
        
        # Extract operation types from relevant rules
        operation_types_in_context = []
        for rule in relevant_rules:
            desc = rule.get('description', '').lower()
            for op_type in self.knowledge_base['operation_types']:
                if op_type in desc and op_type not in operation_types_in_context:
                    operation_types_in_context.append(op_type)
        
        # Extract rule numbers from relevant rules
        relevant_rule_numbers = [r.get('rule_number', '') for r in relevant_rules if r.get('rule_number')]
        
        # Question templates - more diverse endings
        question_templates = [
            # What questions - varied endings
            ("What is {term}?", ['term']),
            ("What are {term}?", ['term']),
            ("What are the {term} limits?", ['term']),
            ("What are the {term} restrictions?", ['term']),
            ("What are the {term} procedures?", ['term']),
            ("What {term} must be met?", ['term']),
            ("What happens if I {action} {term}?", ['action', 'term']),
            ("What {term} are specified?", ['term']),
            ("What are the {term} standards?", ['term']),
            ("What {term} apply?", ['term']),
            
            # How questions - varied
            ("How do I {action} {term}?", ['action', 'term']),
            ("How is {term} determined?", ['term']),
            ("How does {term} work?", ['term']),
            ("How long does {term} take?", ['term']),
            ("How are {term} monitored?", ['term']),
            ("How can I {action} {term}?", ['action', 'term']),
            ("How is {term} measured?", ['term']),
            ("How do {term} differ?", ['term']),
            
            # Are/Is questions - varied
            ("Are there exceptions to {term}?", ['term']),
            ("Are {term} required?", ['term']),
            ("Is {term} allowed?", ['term']),
            ("Are {term} mandatory?", ['term']),
            ("Are there different {term} by {category}?", ['term', 'category']),
            ("Is {term} permitted?", ['term']),
            ("Are {term} necessary?", ['term']),
            
            # Can questions
            ("Can I {action} {term}?", ['action', 'term']),
            ("Can {term} be {action}?", ['term', 'action']),
            ("Can {term} exceed {value}?", ['term', 'value']),
            
            # When questions
            ("When is {term} required?", ['term']),
            ("When must {term} be {action}?", ['term', 'action']),
            ("When can I {action} {term}?", ['action', 'term']),
            
            # Where questions
            ("Where can I {action} {term}?", ['action', 'term']),
            ("Where are {term} allowed?", ['term']),
            
            # Who questions
            ("Who can {action} {term}?", ['action', 'term']),
            ("Who is responsible for {term}?", ['term']),
            ("Who must {action} {term}?", ['action', 'term']),
            
            # Which questions
            ("Which {term} apply?", ['term']),
            ("Which {term} are required?", ['term']),
            
            # Why questions
            ("Why are {term} necessary?", ['term']),
        ]
        
        # Generate candidate questions
        candidate_questions = []
        
        # Extract key terms from query and rules - more diverse extraction
        key_terms = []
        
        # Extract rule titles (often contain key concepts)
        rule_titles = [r.get('title', '').lower().strip('.') for r in relevant_rules[:5] if r.get('title')]
        for title in rule_titles:
            # Extract meaningful words from titles
            title_words = [w for w in re.findall(r'\b\w{4,}\b', title) if w not in ['this', 'that', 'with', 'from']]
            key_terms.extend(title_words[:2])
        
        # Add terms from query (prioritize longer, more specific terms)
        for word in sorted(query_words, key=len, reverse=True):
            if word in self.knowledge_base['important_words'] and len(word) >= 4:
                key_terms.append(word)
        
        # Add terms from relevant rules (prioritize less common words)
        rule_word_freq = Counter(rule_words)
        for word, freq in sorted(rule_word_freq.items(), key=lambda x: x[1]):
            if word in self.knowledge_base['important_words'] and word not in key_terms and len(word) >= 4:
                key_terms.append(word)
                if len(key_terms) >= 15:  # Limit to avoid too many
                    break
        
        # Add key phrases from rules (these are more specific)
        for phrase in self.knowledge_base['key_phrases']:
            if any(word in phrase for word in query_words) or phrase in rule_texts:
                if phrase not in key_terms:
                    key_terms.append(phrase)
        
        # Add operation types
        if operation_types_in_context:
            key_terms.extend(operation_types_in_context[:2])
        
        # Add categories
        if top_categories:
            key_terms.extend([cat.replace('_', ' ') for cat in top_categories[:2]])
        
        # Add numerical values if relevant
        for num_val in self.knowledge_base['numerical_values'][:5]:
            if any(word in num_val.lower() for word in query_words):
                key_terms.append(num_val)
        
        # Remove duplicates while preserving order
        seen_terms = set()
        unique_terms = []
        for term in key_terms:
            term_lower = term.lower()
            if term_lower not in seen_terms:
                seen_terms.add(term_lower)
                unique_terms.append(term)
        key_terms = unique_terms[:20]  # Limit to top 20 most relevant
        
        # Generate questions using templates - smarter generation
        actions = ['apply', 'obtain', 'get', 'conduct', 'perform', 'operate', 'comply', 'meet', 'use', 'exceed', 'violate']
        values = self.knowledge_base['numerical_values'][:5]
        
        # Track which templates we've used to ensure variety
        used_templates = set()
        template_usage = Counter()
        
        # Shuffle templates to get variety
        import random
        shuffled_templates = question_templates.copy()
        random.shuffle(shuffled_templates)
        
        for template, placeholders in shuffled_templates:
            # Limit usage of each template
            template_key = template.split('{')[0]  # Get template prefix
            if template_usage[template_key] >= 3:
                continue
            
            for term in key_terms[:8]:  # Use fewer terms but better ones
                try:
                    if '{term}' in template and '{action}' not in template and '{category}' not in template and '{value}' not in template:
                        question = template.replace('{term}', term)
                        if question not in candidate_questions and len(question) > 15:
                            candidate_questions.append(question)
                            template_usage[template_key] += 1
                            used_templates.add(template)
                    
                    elif '{action}' in template and '{term}' in template:
                        # Use different actions for variety
                        for action in random.sample(actions, min(2, len(actions))):
                            question = template.replace('{action}', action).replace('{term}', term)
                            if question not in candidate_questions and len(question) > 15:
                                candidate_questions.append(question)
                                template_usage[template_key] += 1
                    
                    elif '{category}' in template:
                        for cat in top_categories[:1]:  # Use fewer categories
                            cat_text = cat.replace('_', ' ')
                            question = template.replace('{term}', term).replace('{category}', cat_text)
                            if question not in candidate_questions and len(question) > 15:
                                candidate_questions.append(question)
                                template_usage[template_key] += 1
                    
                    elif '{value}' in template:
                        for val in values[:2]:
                            question = template.replace('{term}', term).replace('{value}', val)
                            if question not in candidate_questions and len(question) > 15:
                                candidate_questions.append(question)
                                template_usage[template_key] += 1
                except:
                    continue
        
        # Generate specific questions based on query context
        context_questions = self._generate_context_specific_questions(query_lower, relevant_rules, top_categories, operation_types_in_context)
        candidate_questions.extend(context_questions)
        
        # Score and rank questions
        scored_questions = []
        for q in candidate_questions:
            score = self._score_question_relevance(q, query_lower, rule_texts, key_terms)
            scored_questions.append((score, q))
        
        # Sort by score and remove duplicates
        scored_questions.sort(reverse=True, key=lambda x: x[0])
        
        # Get top 3 unique questions with variety
        seen = set()
        final_questions = []
        question_starters_used = set()
        
        for score, q in scored_questions:
            q_lower = q.lower()
            q_starter = q_lower.split()[0] if q_lower.split() else ''
            
            # Ensure variety in question types
            if q_lower not in seen and len(q) > 15:  # Filter very short questions
                # Prefer questions with different starters
                if len(final_questions) < 3:
                    if q_starter not in question_starters_used or len(final_questions) >= 2:
                        seen.add(q_lower)
                        question_starters_used.add(q_starter)
                        final_questions.append(q)
                        if len(final_questions) >= 3:
                            break
                else:
                    # If we have 3 but they're all same type, try to diversify
                    if q_starter not in question_starters_used:
                        # Replace lowest scoring question of same type
                        for i, existing_q in enumerate(final_questions):
                            existing_starter = existing_q.lower().split()[0] if existing_q.lower().split() else ''
                            if existing_starter == q_starter:
                                # Check if this is better
                                existing_score = next((s for s, qq in scored_questions if qq == existing_q), 0)
                                if score > existing_score:
                                    final_questions[i] = q
                                    seen.add(q_lower)
                                    break
        
        # Fallback to default if not enough questions
        if len(final_questions) < 3:
            final_questions.extend(self._default_followups()[:3-len(final_questions)])
        
        return final_questions[:3]
    
    def _generate_context_specific_questions(self, query_lower: str, relevant_rules: List[Dict], 
                                            top_categories: List[str], operation_types: List[str]) -> List[str]:
        """Generate context-specific questions based on query and rules"""
        questions = []
        
        # Format category names
        def format_cat(cat):
            return cat.replace('_', ' ').title()
        
        # Weight-related
        if any(word in query_lower for word in ['weight', 'pound', 'lb', 'mass']):
            for op_type in operation_types[:2]:
                questions.append(f"What are weight limits for {op_type} operations?")
            questions.append("Are there different weight limits by permit type?")
            questions.append("What happens if I exceed weight restrictions?")
        
        # Speed-related
        if any(word in query_lower for word in ['speed', 'mph', 'velocity', 'knot']):
            questions.append("What are speed restrictions for BVLOS operations?")
            questions.append("Are there speed limits by operation type?")
            questions.append("What happens if I exceed speed limits?")
        
        # Altitude-related
        if any(word in query_lower for word in ['altitude', 'height', 'feet', 'agl', 'ceiling']):
            questions.append("What are altitude restrictions for BVLOS flights?")
            questions.append("Are there exceptions for altitude limits?")
            questions.append("How is altitude measured and monitored?")
        
        # Permit/Certificate-related
        if any(word in query_lower for word in ['permit', 'certificate', 'license', 'authorization']):
            questions.append("How do I apply for a BVLOS permit?")
            questions.append("What are the requirements for permit approval?")
            questions.append("How long does permit processing take?")
            for op_type in operation_types[:2]:
                questions.append(f"What are the requirements for {op_type} permits?")
        
        # Safety-related
        if any(word in query_lower for word in ['safety', 'risk', 'hazard', 'emergency']):
            questions.append("What safety requirements must be met?")
            questions.append("How are safety risks assessed?")
            questions.append("What emergency procedures are required?")
        
        # Category-specific questions
        for cat in top_categories[:2]:
            cat_text = format_cat(cat)
            questions.append(f"What are the regulations for {cat_text}?")
            questions.append(f"Are there specific requirements for {cat_text}?")
        
        # Operation type questions
        for op_type in operation_types[:2]:
            questions.append(f"What are the requirements for {op_type} operations?")
            questions.append(f"Are there restrictions for {op_type}?")
        
        return questions
    
    def _score_question_relevance(self, question: str, query: str, rule_text: str, key_terms: List[str]) -> float:
        """Score question relevance based on query and context - penalize repetitive patterns"""
        score = 0.0
        q_lower = question.lower()
        
        # Penalize questions ending with "requirements" if we already have one
        if q_lower.endswith('requirements'):
            score -= 1.0
        
        # Check if question contains key terms
        for term in key_terms[:5]:
            if term.lower() in q_lower:
                score += 2.0
        
        # Check if question relates to query
        query_words = set(re.findall(r'\b\w+\b', query))
        q_words = set(re.findall(r'\b\w+\b', q_lower))
        common_words = query_words & q_words
        if common_words:
            score += len(common_words) * 1.5
        
        # Check if question relates to rule text
        if any(word in rule_text for word in q_words if len(word) > 4):
            score += 1.0
        
        # Prefer diverse question types - bonus for different starters
        if q_lower.startswith('how'):
            score += 1.0  # Prefer "how" questions
        elif q_lower.startswith('are') or q_lower.startswith('is'):
            score += 0.8  # Prefer yes/no questions
        elif q_lower.startswith('can'):
            score += 0.7
        elif q_lower.startswith('when'):
            score += 0.6
        elif q_lower.startswith('where'):
            score += 0.6
        elif q_lower.startswith('who'):
            score += 0.6
        elif q_lower.startswith('which'):
            score += 0.5
        elif q_lower.startswith('why'):
            score += 0.5
        elif q_lower.startswith('what'):
            score += 0.3  # Lower score for "what" since they're common
        
        # Penalize very generic questions
        generic_endings = ['requirements', 'regulations', 'rules', 'standards']
        generic_count = sum(1 for ending in generic_endings if q_lower.endswith(ending))
        if generic_count > 0:
            score -= 0.5 * generic_count
        
        # Bonus for specific terms (longer, more specific)
        if any(len(term) > 8 for term in key_terms if term.lower() in q_lower):
            score += 1.5
        
        # Bonus for questions with operation types or categories
        if any(op_type in q_lower for op_type in self.knowledge_base['operation_types']):
            score += 1.0
        
        return score
    
    def _default_followups(self) -> List[str]:
        """Default follow-up questions"""
        return [
            "Can you provide more details?",
            "What are related regulations?",
            "Are there any exceptions?"
        ]
    
    def generate_response(self, query: str, relevant_rules: List[Dict], summary_preference: str = None) -> Dict:
        """Generate response using Google Gemini API, returns dict with response and follow-ups"""
        # Handle greetings
        if self.is_greeting(query):
            return {
                'response': self.handle_greeting(),
                'follow_ups': [
                    "What are weight limits for drones?",
                    "What are the speed restrictions?",
                    "How do I get a BVLOS permit?"
                ]
            }
        
        if not GOOGLE_API_KEY:
            response_text = self._fallback_response(query, relevant_rules, summary_preference)
        else:
        try:
            # Prepare context from relevant rules
            context = "\n\n".join([
                f"Rule {rule.get('rule_number', 'N/A')}: {rule.get('title', 'N/A')}\n"
                f"Category: {rule.get('category', 'N/A')}\n"
                f"Definition: {rule.get('definition', 'N/A')}\n"
                f"Description: {rule.get('description', 'N/A')}"
                for rule in relevant_rules
            ])
            
                # Adjust prompt based on summary preference
                if summary_preference == 'short':
                    length_instruction = """Please provide a CONCISE answer (2-3 sentences maximum). Focus on the key facts and specific rule numbers. Be brief and to the point."""
                elif summary_preference == 'detailed':
                    length_instruction = """Please provide a COMPREHENSIVE and DETAILED answer. Include all relevant information, specific rule numbers, examples, exceptions, and practical implications. Be thorough and complete."""
                else:
                    # Default to detailed if no preference specified
                    length_instruction = """Please provide a clear, detailed answer based on the regulations above. Include specific rule numbers when applicable."""
                
            # Create prompt for Gemini
            prompt = f"""You are an expert drone regulation assistant. Based on the following FAA drone regulations, 
answer the user's question accurately and comprehensively.

RELEVANT REGULATIONS:
{context}

USER QUESTION: {query}

{length_instruction}
If the regulations don't contain enough information to fully answer the question, acknowledge this and provide what information is available."""

            # Use Gemini API (using the correct model name for the API version)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
                response_text = response.text
            
        except Exception as e:
            print(f"Error with Gemini API: {e}")
                response_text = self._fallback_response(query, relevant_rules, summary_preference)
        
        # Generate follow-up questions
        follow_ups = self.generate_followups(query, relevant_rules)
        
        return {
            'response': response_text,
            'follow_ups': follow_ups
        }
    
    def _fallback_response(self, query: str, relevant_rules: List[Dict], summary_preference: str = None) -> str:
        """Fallback response when Gemini API is not available"""
        if not relevant_rules:
            return "I couldn't find any relevant drone regulations for your query. Please try rephrasing your question."
        
        if summary_preference == 'short':
            # Short summary - just key points
            response = f"Based on the regulations:\n\n"
            for i, rule in enumerate(relevant_rules[:2], 1):
                response += f"**Rule {rule.get('rule_number', 'N/A')}**: {rule.get('title', 'N/A')}\n"
                response += f"{rule.get('definition', 'N/A')[:150]}...\n\n"
        else:
            # Detailed response
        response = f"Based on the drone regulations, here's what I found:\n\n"
        for i, rule in enumerate(relevant_rules[:3], 1):
            response += f"{i}. **Rule {rule.get('rule_number', 'N/A')} - {rule.get('title', 'N/A')}**\n"
            response += f"   Category: {rule.get('category', 'N/A')}\n"
            response += f"   {rule.get('definition', 'N/A')[:300]}...\n\n"
        
        response += "\n*Note: Google Gemini API key not configured. Set GOOGLE_API_KEY environment variable for enhanced AI responses.*"
        return response


def format_category_name(category):
    """Format category name for display"""
    return category.replace('_', ' ').title()

# Initialize RAG system
rag_system = DroneRAG()

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def query():
    """Handle user queries"""
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        summary_preference = data.get('summary_preference', None)  # 'short' or 'detailed' or None
        
        if not user_query:
            return jsonify({'error': 'Please provide a query'}), 400
        
        # Find relevant rules (skip for greetings)
        if not rag_system.is_greeting(user_query):
        relevant_rules = rag_system.find_relevant_rules(user_query, top_k=5)
        else:
            relevant_rules = []
        
        # If no summary preference provided, ask the user
        if summary_preference is None and not rag_system.is_greeting(user_query) and relevant_rules:
            return jsonify({
                'ask_summary_preference': True,
                'query': user_query,
                'relevant_rules': [
                    {
                        'rule_number': rule.get('rule_number', 'N/A'),
                        'title': rule.get('title', 'N/A'),
                        'category': rule.get('category', 'N/A'),
                        'similarity_score': rule.get('similarity_score', 0)
                    }
                    for rule in relevant_rules[:3]
                ]
            })
        
        # Generate response (includes follow-ups) with summary preference
        result = rag_system.generate_response(user_query, relevant_rules, summary_preference)
        
        return jsonify({
            'response': result['response'],
            'follow_ups': result.get('follow_ups', []),
            'relevant_rules': [
                {
                    'rule_number': rule.get('rule_number', 'N/A'),
                    'title': rule.get('title', 'N/A'),
                    'category': rule.get('category', 'N/A'),
                    'similarity_score': rule.get('similarity_score', 0)
                }
                for rule in relevant_rules[:3]
            ]
        })
        
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rules', methods=['GET'])
def get_rules():
    """Get all rules or filter by category"""
    try:
        category = request.args.get('category', None)
        
        if category:
            filtered_rules = [r for r in rag_system.rules if r.get('category') == category]
        else:
            filtered_rules = rag_system.rules
        
        return jsonify({
            'rules': filtered_rules[:50],  # Limit to 50 for performance
            'total': len(filtered_rules)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all unique categories"""
    try:
        categories = list(set(rule.get('category', 'unknown') for rule in rag_system.rules))
        return jsonify({'categories': sorted(categories)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
