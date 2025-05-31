const passwordInput = document.getElementById('passwordInput');
        const strengthDisplay = document.getElementById('strengthDisplay');
        let checkTimeout;

        passwordInput.addEventListener('input', function() {
            clearTimeout(checkTimeout);
            checkTimeout = setTimeout(checkPassword, 300); // Debounce
        });

        function togglePasswordVisibility() {
            const input = document.getElementById('passwordInput');
            const button = document.querySelector('.toggle-password');
            
            if (input.type === 'password') {
                input.type = 'text';
                button.textContent = '🙈';
            } else {
                input.type = 'password';
                button.textContent = '👁️';
            }
        }

        async function checkPassword() {
            const password = passwordInput.value;
            
            if (!password) {
                strengthDisplay.style.display = 'none';
                return;
            }
            
            try {
                const response = await fetch('/check', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ password: password })
                });
                
                const result = await response.json();
                updateDisplay(result);
                strengthDisplay.style.display = 'block';
            } catch (error) {
                console.error('Error checking password:', error);
            }
        }

        function updateDisplay(result) {
            // Update strength label and meter
            const strengthLabel = document.getElementById('strengthLabel');
            const strengthFill = document.getElementById('strengthFill');
            
            strengthLabel.textContent = result.strength;
            strengthLabel.className = 'strength-label strength-' + result.strength.toLowerCase().replace(' ', '-');
            
            strengthFill.style.width = result.score + '%';
            strengthFill.className = 'strength-fill strength-' + result.strength.toLowerCase().replace(' ', '-');
            
            // Update stats
            document.getElementById('scoreValue').textContent = result.score;
            document.getElementById('lengthValue').textContent = result.length;
            document.getElementById('entropyValue').textContent = result.entropy;
            
            // Update criteria
            updateCriteria(result.criteria);
            
            // Update feedback
            updateFeedback(result.feedback);
        }

        function updateCriteria(criteria) {
            const criteriaGrid = document.getElementById('criteriaGrid');
            const criteriaMap = {
                'length': 'At least 8 characters',
                'min_length': 'At least 12 characters',
                'uppercase': 'Uppercase letters (A-Z)',
                'lowercase': 'Lowercase letters (a-z)',
                'numbers': 'Numbers (0-9)',
                'special_chars': 'Special characters (!@#$...)',
                'no_common_patterns': 'No common patterns'
            };
            
            criteriaGrid.innerHTML = '';
            
            for (const [key, label] of Object.entries(criteriaMap)) {
                const item = document.createElement('div');
                item.className = 'criteria-item' + (criteria[key] ? ' met' : '');
                item.innerHTML = `
                    <span class="criteria-icon">${criteria[key] ? '✓' : '✗'}</span>
                    <span>${label}</span>
                `;
                criteriaGrid.appendChild(item);
            }
        }

        function updateFeedback(feedback) {
            const feedbackList = document.getElementById('feedbackList');
            feedbackList.innerHTML = '';
            
            feedback.forEach(item => {
                const li = document.createElement('li');
                li.className = 'feedback-item' + (item.includes('Excellent') ? ' positive' : '');
                li.textContent = item;
                feedbackList.appendChild(li);
            });
        }

        function generatePassword() {
            const chars = {
                lowercase: 'abcdefghijklmnopqrstuvwxyz',
                uppercase: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                numbers: '0123456789',
                special: '!@#$%^&*()_+-=[]{}|;:,.<>?'
            };
            
            let password = '';
            const categories = Object.values(chars);
            
            // Ensure at least one character from each category
            for (const category of categories) {
                password += category[Math.floor(Math.random() * category.length)];
            }
            
            // Fill the rest randomly (aim for 16 characters total)
            const allChars = categories.join('');
            for (let i = password.length; i < 16; i++) {
                password += allChars[Math.floor(Math.random() * allChars.length)];
            }
            
            // Shuffle the password
            password = password.split('').sort(() => Math.random() - 0.5).join('');
            
            passwordInput.value = password;
            checkPassword();
        }