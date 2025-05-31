from flask import Flask, render_template, request, jsonify
import re
import math

app = Flask(__name__)

class PasswordChecker:
    def __init__(self):
        self.common_passwords = {
            'password', '123456', '123456789', 'qwerty', 'abc123', 
            'password123', 'admin', 'letmein', 'welcome', 'monkey',
            'dragon', 'master', 'hello', 'freedom', 'whatever',
            'qazwsx', 'trustno1', 'jordan23', 'harley', 'robert'
        }
        
        self.common_patterns = [
            r'123+', r'abc+', r'qwe+', r'asd+', r'zxc+',
            r'(.)\1{2,}',  # repeated characters
            r'password', r'admin', r'user', r'login'
        ]
    
    def calculate_entropy(self, password):
        """Calculate password entropy"""
        charset_size = 0
        
        if re.search(r'[a-z]', password):
            charset_size += 26
        if re.search(r'[A-Z]', password):
            charset_size += 26
        if re.search(r'[0-9]', password):
            charset_size += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            charset_size += 32
        
        if charset_size == 0:
            return 0
        
        return len(password) * math.log2(charset_size)
    
    def check_common_patterns(self, password):
        """Check for common weak patterns"""
        issues = []
        
        # Check against common passwords
        if password.lower() in self.common_passwords:
            issues.append("This is a commonly used password")
        
        # Check for common patterns
        for pattern in self.common_patterns:
            if re.search(pattern, password.lower()):
                if 'repeated characters' in pattern:
                    issues.append("Contains repeated characters")
                elif any(word in pattern for word in ['password', 'admin', 'user', 'login']):
                    issues.append("Contains common words")
                else:
                    issues.append("Contains common keyboard patterns")
        
        # Check for keyboard walks
        keyboard_rows = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm', '1234567890']
        for row in keyboard_rows:
            for i in range(len(row) - 2):
                if row[i:i+3] in password.lower():
                    issues.append("Contains keyboard sequences")
                    break
        
        return issues
    
    def assess_password(self, password):
        """Main password assessment function"""
        if not password:
            return {
                'score': 0,
                'strength': 'No Password',
                'feedback': ['Please enter a password'],
                'criteria': self.get_empty_criteria()
            }
        
        criteria = {
            'length': len(password) >= 8,
            'min_length': len(password) >= 12,
            'uppercase': bool(re.search(r'[A-Z]', password)),
            'lowercase': bool(re.search(r'[a-z]', password)),
            'numbers': bool(re.search(r'[0-9]', password)),
            'special_chars': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
            'no_common_patterns': len(self.check_common_patterns(password)) == 0
        }
        
        # Calculate base score
        score = 0
        
        # Length scoring
        if len(password) >= 16:
            score += 25
        elif len(password) >= 12:
            score += 20
        elif len(password) >= 8:
            score += 15
        elif len(password) >= 6:
            score += 10
        else:
            score += 5
        
        # Character variety scoring
        if criteria['uppercase']:
            score += 10
        if criteria['lowercase']:
            score += 10
        if criteria['numbers']:
            score += 10
        if criteria['special_chars']:
            score += 15
        
        # Entropy bonus
        entropy = self.calculate_entropy(password)
        if entropy > 60:
            score += 20
        elif entropy > 40:
            score += 15
        elif entropy > 25:
            score += 10
        
        # Pattern penalties
        pattern_issues = self.check_common_patterns(password)
        score -= len(pattern_issues) * 10
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        # Determine strength level
        if score >= 80:
            strength = 'Very Strong'
        elif score >= 60:
            strength = 'Strong'
        elif score >= 40:
            strength = 'Moderate'
        elif score >= 20:
            strength = 'Weak'
        else:
            strength = 'Very Weak'
        
        # Generate feedback
        feedback = self.generate_feedback(password, criteria, pattern_issues)
        
        return {
            'score': score,
            'strength': strength,
            'feedback': feedback,
            'criteria': criteria,
            'entropy': round(entropy, 1),
            'length': len(password)
        }
    
    def generate_feedback(self, password, criteria, pattern_issues):
        """Generate specific feedback for password improvement"""
        feedback = []
        
        # Length feedback
        if len(password) < 8:
            feedback.append("Password should be at least 8 characters long")
        elif len(password) < 12:
            feedback.append("Consider using 12+ characters for better security")
        
        # Character type feedback
        if not criteria['uppercase']:
            feedback.append("Add uppercase letters (A-Z)")
        if not criteria['lowercase']:
            feedback.append("Add lowercase letters (a-z)")
        if not criteria['numbers']:
            feedback.append("Add numbers (0-9)")
        if not criteria['special_chars']:
            feedback.append("Add special characters (!@#$%^&*)")
        
        # Add pattern issues
        feedback.extend(pattern_issues)
        
        # Positive feedback for strong passwords
        if not feedback:
            feedback.append("Excellent! This is a strong password.")
        
        return feedback
    
    def get_empty_criteria(self):
        """Return empty criteria structure"""
        return {
            'length': False,
            'min_length': False,
            'uppercase': False,
            'lowercase': False,
            'numbers': False,
            'special_chars': False,
            'no_common_patterns': False
        }

# Initialize password checker
password_checker = PasswordChecker()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_password():
    data = request.get_json()
    password = data.get('password', '')
    result = password_checker.assess_password(password)
    return jsonify(result)

@app.route('/api/check/<password>')
def api_check(password):
    """API endpoint for direct password checking"""
    result = password_checker.assess_password(password)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)