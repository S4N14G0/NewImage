 // Variables globales
        let currentTab = 'login';

        // Cambiar entre tabs
        function switchTab(tab) {
            currentTab = tab;
            
            // Actualizar tabs
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelector(`.tab:${tab === 'login' ? 'first' : 'last'}-child`).classList.add('active');
            
            // Actualizar formularios
            document.querySelectorAll('.form').forEach(f => f.classList.remove('active'));
            document.getElementById(tab + 'Form').classList.add('active');
            
            // Limpiar errores
            clearErrors();
        }

        // Toggle password visibility
        function togglePassword(fieldId) {
            const field = document.getElementById(fieldId);
            const toggle = field.nextElementSibling;
            
            if (field.type === 'password') {
                field.type = 'text';
                toggle.textContent = '🙈';
            } else {
                field.type = 'password';
                toggle.textContent = '👁';
            }
        }

        // Validaciones
        function validateEmail(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        }

        function validatePassword(password) {
            return password.length >= 8;
        }

        function validateName(name) {
            return name.trim().length >= 2;
        }

        // Mostrar errores
        function showError(fieldId, message) {
            const field = document.getElementById(fieldId);
            const error = document.getElementById(fieldId + 'Error');
            
            field.classList.add('error');
            error.textContent = message;
            error.style.display = 'block';
        }

        function showSuccess(fieldId) {
            const field = document.getElementById(fieldId);
            field.classList.remove('error');
            field.classList.add('success');
        }

        function clearErrors() {
            document.querySelectorAll('.form-input').forEach(input => {
                input.classList.remove('error', 'success');
            });
            document.querySelectorAll('.error-message').forEach(error => {
                error.style.display = 'none';
            });
        }

        // Mostrar notificaciones
        function showNotification(message, type = 'success') {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => notification.classList.add('show'), 100);
            
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => document.body.removeChild(notification), 300);
            }, 3000);
        }

        // Mostrar loading
        function showLoading(formId, show) {
            const form = document.getElementById(formId);
            const button = form.querySelector('.form-button');
            const text = button.querySelector('.button-text');
            const loading = button.querySelector('.loading');
            
            if (show) {
                button.disabled = true;
                text.style.opacity = '0';
                loading.style.display = 'block';
            } else {
                button.disabled = false;
                text.style.opacity = '1';
                loading.style.display = 'none';
            }
        }

        // Handle Login
        // async function handleLogin(e) {
        //     e.preventDefault();
        //     clearErrors();
            
        //     const email = document.getElementById('loginEmail').value;
        //     const password = document.getElementById('loginPassword').value;
            
        //     let hasErrors = false;
            
        //     // Validaciones
        //     if (!validateEmail(email)) {
        //         showError('loginEmail', 'Por favor ingresa un email válido');
        //         hasErrors = true;
        //     }
            
        //     if (!validatePassword(password)) {
        //         showError('loginPassword', 'La contraseña debe tener al menos 8 caracteres');
        //         hasErrors = true;
        //     }
            
        //     if (hasErrors) return;
            
        //     showLoading('loginForm', true);
            
        //     // Simular delay de API
        //     await new Promise(resolve => setTimeout(resolve, 1500));
            
        //     // Buscar usuario
        //     const user = users.find(u => u.email === email && u.password === password);
            
        //     showLoading('loginForm', false);
            
        //     if (user) {
        //         currentUser = user;
        //         localStorage.setItem('currentUser', JSON.stringify(user));
        //         showNotification('¡Inicio de sesión exitoso!');
        //         setTimeout(showDashboard, 1000);
        //     } else {
        //         showError('loginEmail', 'Email o contraseña incorrectos');
        //         showError('loginPassword', 'Email o contraseña incorrectos');
        //         showNotification('Credenciales inválidas', 'error');
        //     }
        // }

        // // Handle Signup
        // async function handleSignup(e) {
        //     e.preventDefault();
        //     clearErrors();
            
        //     const name = document.getElementById('signupName').value;
        //     const email = document.getElementById('signupEmail').value;
        //     const password = document.getElementById('signupPassword').value;
        //     const confirmPassword = document.getElementById('confirmPassword').value;
            
        //     let hasErrors = false;
            
        //     // Validaciones
        //     if (!validateName(name)) {
        //         showError('signupName', 'El nombre debe tener al menos 2 caracteres');
        //         hasErrors = true;
        //     }
            
        //     if (!validateEmail(email)) {
        //         showError('signupEmail', 'Por favor ingresa un email válido');
        //         hasErrors = true;
        //     }
            
        //     if (!validatePassword(password)) {
        //         showError('signupPassword', 'La contraseña debe tener al menos 8 caracteres');
        //         hasErrors = true;
        //     }
            
        //     if (password !== confirmPassword) {
        //         showError('confirmPassword', 'Las contraseñas no coinciden');
        //         hasErrors = true;
        //     }
            
        //     // Verificar si el usuario ya existe
        //     if (users.find(u => u.email === email)) {
        //         showError('signupEmail', 'Este email ya está registrado');
        //         hasErrors = true;
        //     }
            
        //     if (hasErrors) return;
            
        //     showLoading('signupForm', true);
            
        //     // Simular delay de API
        //     await new Promise(resolve => setTimeout(resolve, 2000));
            
        //     // Crear nuevo usuario
        //     const newUser = {
        //         id: Date.now(),
        //         name: name,
        //         email: email,
        //         password: password,
        //         createdAt: new Date().toISOString()
        //     };
            
        //     users.push(newUser);
        //     localStorage.setItem('users', JSON.stringify(users));
            
        //     currentUser = newUser;
        //     localStorage.setItem('currentUser', JSON.stringify(newUser));
            
        //     showLoading('signupForm', false);
        //     showNotification('¡Cuenta creada exitosamente!');
        //     setTimeout(showDashboard, 1000);
        // }

        // Mostrar dashboard
        function showDashboard() {
            document.getElementById('authSection').style.display = 'none';
            document.getElementById('dashboard').classList.add('active');
            
            // Actualizar información del usuario
            document.getElementById('userName').textContent = currentUser.name;
            document.getElementById('userEmail').textContent = currentUser.email;
            document.getElementById('userAvatar').textContent = currentUser.name.charAt(0).toUpperCase();
        }

        // Logout
        function logout() {
            currentUser = null;
            localStorage.removeItem('currentUser');
            
            document.getElementById('dashboard').classList.remove('active');
            document.getElementById('authSection').style.display = 'block';
            
            // Limpiar formularios
            document.getElementById('loginForm').reset();
            document.getElementById('signupForm').reset();
            clearErrors();
            
            showNotification('Sesión cerrada correctamente');
        }

        // Social login (simulado)
        function socialLogin(provider) {
            showNotification(`Funcionalidad de ${provider} en desarrollo`, 'error');
        }

        // Forgot password (simulado)
        function showForgotPassword() {
            showNotification('Funcionalidad de recuperación en desarrollo', 'error');
        }

        // Validación en tiempo real
        document.addEventListener('input', function(e) {
            if (e.target.classList.contains('form-input')) {
                const fieldId = e.target.id;
                const value = e.target.value;
                
                // Limpiar errores previos
                e.target.classList.remove('error', 'success');
                document.getElementById(fieldId + 'Error').style.display = 'none';
                
                // Validar según el campo
                let isValid = false;
                
                if (fieldId.includes('Email')) {
                    isValid = validateEmail(value);
                } else if (fieldId.includes('Password')) {
                    isValid = validatePassword(value);
                } else if (fieldId.includes('Name')) {
                    isValid = validateName(value);
                } else if (fieldId === 'confirmPassword') {
                    const password = document.getElementById('signupPassword').value;
                    isValid = value === password && value.length > 0;
                }
                
                if (value.length > 0) {
                    if (isValid) {
                        showSuccess(fieldId);
                    }
                }
            }
        });
