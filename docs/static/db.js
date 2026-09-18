// Midad Academy LMS - Central Persistent Database & Auth System
(function(window) {
    const DB_KEYS = {
        USERS: 'midad_db_users',
        SESSION: 'midad_session',
        NOTIFICATIONS: 'midad_db_notifications',
        VIRTUAL_ROOMS: 'midad_db_virtual_rooms',
        QUIZ_RESULTS: 'midad_db_quiz_results',
        ASSIGNMENT_SUBMISSIONS: 'midad_db_assignment_submissions',
        THEME: 'midad_theme'
    };

    // Default Seed Users
    const SEED_USERS = [
        {
            id: 'u-admin-1',
            name: 'Omar Duhaim',
            email: 'omardohim@gmail.com',
            password: 'AdminPass2026!',
            role: 'admin',
            title: 'Master Super Administrator & Educational Director',
            avatar: './static/images/omar_avatar.png'
        },
        {
            id: 'u-admin-2',
            name: 'Omar Duhaim',
            email: 'admin@lms.local',
            password: 'AdminPass2026!',
            role: 'admin',
            title: 'Master Super Administrator',
            avatar: './static/images/omar_avatar.png'
        },
        {
            id: 'u-student-1',
            name: 'John Doe',
            email: 'john@example.com',
            password: 'StudentPass2026!',
            role: 'student',
            title: 'Medical Scholar',
            avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150'
        },
        {
            id: 'u-student-2',
            name: 'Jane Smith',
            email: 'jane@example.com',
            password: 'StudentPass2026!',
            role: 'student',
            title: 'Clinical Neuroscience Fellow',
            avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150'
        }
    ];

    // Default Seed Virtual Rooms
    const SEED_ROOMS = [
        {
            id: 1,
            title: 'USMLE Step 1 Clinical Pharmacology Review',
            platform: 'Zoom',
            host: 'Omar Duhaim',
            access: 'Passkey',
            passkey: '2026',
            link: 'https://zoom.us/j/987654321',
            time: 'Live Today at 7:00 PM'
        },
        {
            id: 2,
            title: 'Neuroimaging Diagnostic Case Study',
            platform: 'Google Meet',
            host: 'Dr. Sarah Al-Omari',
            access: 'Free',
            passkey: '',
            link: 'https://meet.google.com/abc-defg-hij',
            time: 'Live Today at 8:30 PM'
        }
    ];

    // Seed Initial Data if not present
    function initDatabase() {
        if (!localStorage.getItem(DB_KEYS.USERS)) {
            localStorage.setItem(DB_KEYS.USERS, JSON.stringify(SEED_USERS));
        }
        if (!localStorage.getItem(DB_KEYS.VIRTUAL_ROOMS)) {
            localStorage.setItem(DB_KEYS.VIRTUAL_ROOMS, JSON.stringify(SEED_ROOMS));
        }
        if (!localStorage.getItem(DB_KEYS.NOTIFICATIONS)) {
            const initialNotifs = [
                {
                    id: 1,
                    userEmail: 'all',
                    title: 'New Lecture Available',
                    body: 'Lecture 4: Clinical Pharmacology & Toxicology is now live.',
                    time: '15m ago',
                    unread: true,
                    action: 'courses'
                },
                {
                    id: 2,
                    userEmail: 'all',
                    title: 'Action Required: Quiz Pending',
                    body: 'Lecture 4 Inter-Lecture Quiz is awaiting your submission.',
                    time: '1h ago',
                    unread: true,
                    action: 'quizzes'
                },
                {
                    id: 3,
                    userEmail: 'all',
                    title: 'Clinical Assignment Due',
                    body: 'Neuroimaging Case Study assignment is due in 3 days.',
                    time: '3h ago',
                    unread: true,
                    action: 'assignments'
                }
            ];
            localStorage.setItem(DB_KEYS.NOTIFICATIONS, JSON.stringify(initialNotifs));
        }
    }

    // Initialize immediately
    initDatabase();

    // The MidadDB Public API
    window.MidadDB = {
        // Auth Methods
        authenticate: function(email, password) {
            initDatabase();
            const cleanEmail = (email || '').trim().toLowerCase();
            const cleanPass = (password || '').trim();

            const users = JSON.parse(localStorage.getItem(DB_KEYS.USERS) || '[]');
            const user = users.find(u => u.email.toLowerCase() === cleanEmail);

            if (!user) {
                return {
                    success: false,
                    message: 'No account found with this email address. Please register a new account.'
                };
            }

            if (user.password !== cleanPass) {
                return {
                    success: false,
                    message: 'Incorrect password. Please try again or reset your password.'
                };
            }

            // Valid login! Save active session
            localStorage.setItem(DB_KEYS.SESSION, JSON.stringify(user));
            return {
                success: true,
                user: user
            };
        },

        register: function(name, email, password) {
            initDatabase();
            const cleanName = (name || '').trim();
            const cleanEmail = (email || '').trim().toLowerCase();
            const cleanPass = (password || '').trim();

            if (!cleanName || !cleanEmail || !cleanPass) {
                return { success: false, message: 'Please complete all required fields.' };
            }

            if (cleanPass.length < 6) {
                return { success: false, message: 'Password must be at least 6 characters long.' };
            }

            const users = JSON.parse(localStorage.getItem(DB_KEYS.USERS) || '[]');
            if (users.some(u => u.email.toLowerCase() === cleanEmail)) {
                return { success: false, message: 'An account with this email already exists. Please sign in.' };
            }

            const newUser = {
                id: 'u-' + Date.now(),
                name: cleanName,
                email: cleanEmail,
                password: cleanPass,
                role: 'student', // All public registrations are students
                title: 'Enrolled Student',
                avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150',
                enrolledCourses: ['c1', 'c2']
            };

            users.push(newUser);
            localStorage.setItem(DB_KEYS.USERS, JSON.stringify(users));

            // Log user in automatically
            localStorage.setItem(DB_KEYS.SESSION, JSON.stringify(newUser));

            // Welcome notification
            this.addNotification(cleanEmail, {
                title: 'Welcome to Midad Academy LMS!',
                body: 'Your student account is active. Explore enrolled courses and lectures.',
                action: 'courses'
            });

            return { success: true, user: newUser };
        },

        getCurrentUser: function() {
            const sess = localStorage.getItem(DB_KEYS.SESSION);
            if (!sess) return null;
            try { return JSON.parse(sess); } catch(e) { return null; }
        },

        logout: function() {
            localStorage.removeItem(DB_KEYS.SESSION);
            window.location.href = './login.html';
        },

        requireAdmin: function() {
            const user = this.getCurrentUser();
            if (!user) {
                window.location.href = './login.html';
                return false;
            }
            if (user.role !== 'admin') {
                alert('Access Denied: Creator Studio and Admin Settings are restricted exclusively to Administrator Omar Duhaim. Redirecting to your Student Learning Portal...');
                window.location.href = './student.html';
                return false;
            }
            return true;
        },

        requireStudent: function() {
            const user = this.getCurrentUser();
            if (!user) {
                window.location.href = './login.html';
                return false;
            }
            return true;
        },

        // Notifications System
        getNotifications: function(userEmail) {
            initDatabase();
            const all = JSON.parse(localStorage.getItem(DB_KEYS.NOTIFICATIONS) || '[]');
            return all.filter(n => n.userEmail === 'all' || n.userEmail === userEmail);
        },

        getUnreadCount: function(userEmail) {
            return this.getNotifications(userEmail).filter(n => n.unread).length;
        },

        markAllRead: function(userEmail) {
            const all = JSON.parse(localStorage.getItem(DB_KEYS.NOTIFICATIONS) || '[]');
            all.forEach(n => {
                if (n.userEmail === 'all' || n.userEmail === userEmail) {
                    n.unread = false;
                }
            });
            localStorage.setItem(DB_KEYS.NOTIFICATIONS, JSON.stringify(all));
        },

        addNotification: function(userEmail, notif) {
            const all = JSON.parse(localStorage.getItem(DB_KEYS.NOTIFICATIONS) || '[]');
            all.unshift({
                id: Date.now(),
                userEmail: userEmail,
                title: notif.title,
                body: notif.body,
                time: 'Just now',
                unread: true,
                action: notif.action || 'courses'
            });
            localStorage.setItem(DB_KEYS.NOTIFICATIONS, JSON.stringify(all));
        },

        // Quizzes System
        getQuizStatus: function(userEmail, quizId) {
            const results = JSON.parse(localStorage.getItem(DB_KEYS.QUIZ_RESULTS) || '{}');
            const key = userEmail + '_' + quizId;
            return results[key] || null;
        },

        submitQuiz: function(userEmail, quizId, quizTitle, score, passed) {
            const results = JSON.parse(localStorage.getItem(DB_KEYS.QUIZ_RESULTS) || '{}');
            const key = userEmail + '_' + quizId;
            results[key] = {
                quizId: quizId,
                title: quizTitle,
                score: score,
                passed: passed,
                completedAt: new Date().toISOString()
            };
            localStorage.setItem(DB_KEYS.QUIZ_RESULTS, JSON.stringify(results));

            // Generate real notification
            this.addNotification(userEmail, {
                title: 'Quiz Completed: ' + quizTitle,
                body: 'Your evaluation score: ' + score + '% (' + (passed ? 'Passed' : 'Needs Review') + '). Recorded in your academic transcript.',
                action: 'quizzes'
            });
        },

        // Assignments System
        getAssignmentStatus: function(userEmail, assignmentId) {
            const subs = JSON.parse(localStorage.getItem(DB_KEYS.ASSIGNMENT_SUBMISSIONS) || '{}');
            const key = userEmail + '_' + assignmentId;
            return subs[key] || null;
        },

        submitAssignment: function(userEmail, assignmentId, title, notes, fileName) {
            const subs = JSON.parse(localStorage.getItem(DB_KEYS.ASSIGNMENT_SUBMISSIONS) || '{}');
            const key = userEmail + '_' + assignmentId;
            subs[key] = {
                assignmentId: assignmentId,
                title: title,
                notes: notes,
                fileName: fileName || 'Case_Evaluation.pdf',
                status: 'Submitted',
                submittedAt: new Date().toISOString(),
                grade: 'Pending Review'
            };
            localStorage.setItem(DB_KEYS.ASSIGNMENT_SUBMISSIONS, JSON.stringify(subs));

            this.addNotification(userEmail, {
                title: 'Assignment Submitted: ' + title,
                body: 'File "' + (fileName || 'Case_Evaluation.pdf') + '" received. Submitted for faculty evaluation by Dr. Omar Duhaim.',
                action: 'assignments'
            });
        },

        // Virtual Rooms
        getVirtualRooms: function() {
            initDatabase();
            return JSON.parse(localStorage.getItem(DB_KEYS.VIRTUAL_ROOMS) || '[]');
        },

        addVirtualRoom: function(room) {
            const rooms = this.getVirtualRooms();
            rooms.unshift(room);
            localStorage.setItem(DB_KEYS.VIRTUAL_ROOMS, JSON.stringify(rooms));

            // Push notification to all students
            this.addNotification('all', {
                title: 'Live Study Room: ' + room.title,
                body: 'Hosted by ' + room.host + ' on ' + room.platform + ' (' + room.access + '). Click to join.',
                action: 'meetings'
            });
        }
    };
})(window);
