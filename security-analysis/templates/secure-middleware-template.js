// middlewares/security.js
// Security middleware template for Express.js applications

const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const cors = require('cors');
const bcrypt = require('bcrypt');
const crypto = require('crypto');

/**
 * Rate limiting middleware
 * Prevents brute force attacks and API abuse
 */
const createRateLimiter = (windowMs = 15 * 60 * 1000, max = 100, message = 'Too many requests') => {
  return rateLimit({
    windowMs,
    max,
    message: {
      error: 'Too many requests from this IP, please try again later.',
      retryAfter: Math.ceil(windowMs / 1000)
    },
    standardHeaders: true,
    legacyHeaders: false,
  });
};

/**
 * Security headers middleware
 * Implements various security headers to protect against common attacks
 */
const securityHeaders = helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'"],
      fontSrc: ["'self'"],
      objectSrc: ["'none'"],
      mediaSrc: ["'self'"],
      frameSrc: ["'none'"],
    },
  },
  crossOriginEmbedderPolicy: false,
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
});

/**
 * CORS configuration
 * Restricts cross-origin requests to trusted domains
 */
const corsOptions = {
  origin: function (origin, callback) {
    const allowedOrigins = process.env.ALLOWED_ORIGINS ? 
      process.env.ALLOWED_ORIGINS.split(',') : 
      ['http://localhost:3000', 'http://localhost:3001'];
    
    // Allow requests with no origin (like mobile apps or curl requests)
    if (!origin) return callback(null, true);
    
    if (allowedOrigins.indexOf(origin) !== -1) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  exposedHeaders: ['X-Total-Count']
};

/**
 * Input sanitization middleware
 * Sanitizes user input to prevent XSS and other injection attacks
 */
const sanitizeInput = (req, res, next) => {
  const escapeHtml = (text) => {
    const map = {
      '&': '&',
      '<': '<',
      '>': '>',
      '"': '"',
      "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
  };

  const sanitizeObject = (obj) => {
    for (let key in obj) {
      if (typeof obj[key] === 'string') {
        obj[key] = escapeHtml(obj[key]);
      } else if (typeof obj[key] === 'object' && obj[key] !== null) {
        sanitizeObject(obj[key]);
      }
    }
  };

  // Sanitize query parameters, body, and params
  if (req.query) sanitizeObject(req.query);
  if (req.body) sanitizeObject(req.body);
  if (req.params) sanitizeObject(req.params);

  next();
};

/**
 * Request size limiting middleware
 * Prevents large payload attacks
 */
const requestSizeLimit = (size = '10mb') => {
  return (req, res, next) => {
    const contentLength = parseInt(req.headers['content-length']);
    const maxSize = 10 * 1024 * 1024; // 10MB default

    if (contentLength && contentLength > maxSize) {
      return res.status(413).json({
        error: 'Request entity too large',
        message: `Request size cannot exceed ${maxSize / (1024 * 1024)}MB`
      });
    }

    next();
  };
};

/**
 * Security logging middleware
 * Logs security-related events and suspicious activities
 */
const securityLogger = (req, res, next) => {
  const logSecurityEvent = (event, details) => {
    console.log(JSON.stringify({
      timestamp: new Date().toISOString(),
      event,
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      url: req.originalUrl,
      method: req.method,
      userId: req.user?.id || 'anonymous',
      details
    }));
  };

  // Log suspicious user agents
  const suspiciousUserAgents = [
    /sqlmap/i,
    /nikto/i,
    /nmap/i,
    /burp/i,
    /zap/i,
    /scanner/i
  ];

  const userAgent = req.get('User-Agent') || '';
  if (suspiciousUserAgents.some(pattern => pattern.test(userAgent))) {
    logSecurityEvent('suspicious_user_agent', { userAgent });
  }

  // Log failed authentication attempts
  res.on('finish', () => {
    if (res.statusCode === 401 || res.statusCode === 403) {
      logSecurityEvent('authentication_failure', {
        statusCode: res.statusCode,
        path: req.path
      });
    }
  });

  next();
};

/**
 * Password strength validation
 */
const validatePasswordStrength = (password) => {
  const errors = [];

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  }

  if (!/(?=.*[a-z])/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }

  if (!/(?=.*[A-Z])/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }

  if (!/(?=.*\d)/.test(password)) {
    errors.push('Password must contain at least one number');
  }

  if (!/(?=.*[!@#$%^&*(),.?":{}|<>])/.test(password)) {
    errors.push('Password must contain at least one special character');
  }

  return errors;
};

/**
 * Secure password hashing
 */
const hashPassword = async (password) => {
  const saltRounds = 12;
  return await bcrypt.hash(password, saltRounds);
};

/**
 * Secure password verification
 */
const verifyPassword = async (password, hash) => {
  return await bcrypt.compare(password, hash);
};

/**
 * Generate secure tokens
 */
const generateSecureToken = (length = 32) => {
  return crypto.randomBytes(length).toString('hex');
};

/**
 * Validate email format
 */
const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate UUID format
 */
const validateUUID = (uuid) => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
};

/**
 * SQL injection detection
 */
const detectSQLInjection = (input) => {
  const sqlPatterns = [
    /(\bselect\b|\binsert\b|\bupdate\b|\bdelete\b|\bdrop\b|\bunion\b|\bexec\b|\bexecute\b)/i,
    /('|(\\')|(;)|(--)|(\||(\*|%|_)))/,
    /(\bor\b|\band\b)\s+\w+\s*[=<>]/i
  ];

  if (typeof input === 'string') {
    return sqlPatterns.some(pattern => pattern.test(input));
  }

  if (typeof input === 'object' && input !== null) {
    return Object.values(input).some(value => detectSQLInjection(value));
  }

  return false;
};

/**
 * XSS detection
 */
const detectXSS = (input) => {
  const xssPatterns = [
    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
    /javascript:/gi,
    /on\w+\s*=/gi,
    /<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi,
    /<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi
  ];

  if (typeof input === 'string') {
    return xssPatterns.some(pattern => pattern.test(input));
  }

  if (typeof input === 'object' && input !== null) {
    return Object.values(input).some(value => detectXSS(value));
  }

  return false;
};

module.exports = {
  createRateLimiter,
  securityHeaders,
  corsOptions,
  sanitizeInput,
  requestSizeLimit,
  securityLogger,
  validatePasswordStrength,
  hashPassword,
  verifyPassword,
  generateSecureToken,
  validateEmail,
  validateUUID,
  detectSQLInjection,
  detectXSS
};