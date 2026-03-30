// js/auth.js — Dummy authentication logic for FindX Chatbot

const FINDX_USER_KEY = 'findx_user';

/**
 * Check if user is logged in. If not, redirect to index.html.
 * Call this at the top of protected pages (chat.html, dashboard.html).
 */
function requireAuth() {
  const user = getUser();
  if (!user) {
    window.location.href = '/app/';
  }
  return user;
}

/**
 * Get current user from localStorage.
 */
function getUser() {
  try {
    const raw = localStorage.getItem(FINDX_USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

/**
 * Perform login (dummy — no real password check).
 * Stores user in localStorage and redirects to chat.html.
 */
function login(email, password) {
  if (!email || !password) return { success: false, message: 'Please fill in all fields.' };
  if (password.length < 4)  return { success: false, message: 'Password must be at least 4 characters.' };

  // Derive display name from email
  const namePart  = email.split('@')[0].replace(/[._-]/g, ' ');
  const name      = namePart.replace(/\b\w/g, c => c.toUpperCase());
  const initials  = name.split(' ').map(p => p[0]).join('').slice(0, 2).toUpperCase();

  const user = {
    email,
    name,
    initials,
    role: 'Knowledge Analyst',
    loginAt: new Date().toISOString()
  };

  localStorage.setItem(FINDX_USER_KEY, JSON.stringify(user));
  return { success: true, user };
}

/**
 * Log out and redirect to landing page.
 */
function logout() {
  localStorage.removeItem(FINDX_USER_KEY);
  // Support both file:// and http:// serving
  window.location.href = '/app/';
}

/**
 * Populate user info in the sidebar/header using stored user object.
 */
function populateUserUI(user) {
  const nameEls     = document.querySelectorAll('[data-user-name]');
  const roleEls     = document.querySelectorAll('[data-user-role]');
  const initialsEls = document.querySelectorAll('[data-user-initials]');
  const emailEls    = document.querySelectorAll('[data-user-email]');

  nameEls.forEach(el     => el.textContent = user.name);
  roleEls.forEach(el     => el.textContent = user.role);
  initialsEls.forEach(el => el.textContent = user.initials);
  emailEls.forEach(el    => el.textContent = user.email);
}
