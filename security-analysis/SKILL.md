---
name: security-analysis
description: Analyze code for security vulnerabilities and best practices. Use when reviewing code for security issues, identifying vulnerabilities, or implementing security measures like input validation, authentication, authorization, and data protection.
---

# Security Analysis

This skill provides comprehensive security analysis for code, focusing on identifying vulnerabilities, implementing security best practices, and ensuring robust protection against common threats.

## Security Analysis Checklist

Use this checklist when analyzing code for security issues:

### 1. Input Validation & Sanitization
- [ ] All user inputs are validated on the server-side
- [ ] Input length limits are enforced
- [ ] Special characters are properly escaped
- [ ] SQL injection prevention measures are in place
- [ ] XSS protection is implemented
- [ ] File upload validation includes type and size checks

### 2. Authentication & Authorization
- [ ] Passwords are hashed (never stored in plain text)
- [ ] JWT tokens have proper expiration times
- [ ] Role-based access control is implemented
- [ ] Session management follows best practices
- [ ] Rate limiting is implemented for login attempts
- [ ] Two-factor authentication is available where appropriate

### 3. Data Protection
- [ ] Sensitive data is encrypted in transit (HTTPS)
- [ ] Sensitive data is encrypted at rest
- [ ] Database credentials are not hardcoded
- [ ] API keys and secrets are properly managed
- [ ] Sensitive information is not logged
- [ ] Data retention policies are followed

### 4. Error Handling
- [ ] Generic error messages don't expose system details
- [ ] Stack traces are not shown to end users
- [ ] Error logging doesn't include sensitive data
- [ ] Failed operations don't leak information

### 5. Dependencies & Libraries
- [ ] All dependencies are up to date
- [ ] No known vulnerabilities in dependencies
- [ ] Only necessary packages are installed
- [ ] Supply chain security is considered

## Common Security Vulnerabilities

### SQL Injection
**Risk**: Malicious SQL code execution
**Prevention**:
```javascript
// ❌ Vulnerable
const query = `SELECT * FROM users WHERE id = ${req.params.id}`;

// ✅ Secure - Use parameterized queries
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [req.params.id]);
```

### Cross-Site Scripting (XSS)
**Risk**: Malicious script execution in browser
**Prevention**:
```javascript
// ❌ Vulnerable
res.send(`<div>${userInput}</div>`);

// ✅ Secure - Escape output
const escapeHtml = require('escape-html');
res.send(`<div>${escapeHtml(userInput)}</div>`);
```

### Cross-Site Request Forgery (CSRF)
**Risk**: Unauthorized actions performed on behalf of users
**Prevention**:
```javascript
// Use CSRF tokens
const csrf = require('csurf');
const csrfProtection = csrf({ cookie: true });

app.use(csrfProtection);
app.get('/form', (req, res) => {
  res.render('send', { csrfToken: req.csrfToken() });
});
```

### Insecure Direct Object References
**Risk**: Access to unauthorized data through parameter manipulation
**Prevention**:
```javascript
// ❌ Vulnerable
app.get('/user/:id', async (req, res) => {
  const user = await User.findByPk(req.params.id);
  res.json(user);
});

// ✅ Secure - Check ownership/permissions
app.get('/user/:id', auth(), async (req, res) => {
  const user = await User.findByPk(req.params.id);
  if (!user || user.id !== req.user.id) {
    return sendError(res, 'Access denied', 403);
  }
  res.json(user);
});
```

### Sensitive Data Exposure
**Risk**: Unauthorized access to sensitive information
**Prevention**:
```javascript
// ❌ Exposing sensitive data
User.findAll().then(users => res.json(users));

// ✅ Filter sensitive data
User.findAll({
  attributes: { exclude: ['password', 'ssn', 'creditCard'] }
}).then(users => res.json(users));
```

## Security Best Practices

### Environment Variables
```javascript
// ❌ Hardcoded secrets
const jwtSecret = 'my-secret-key';

// ✅ Environment variables
const jwtSecret = process.env.JWT_SECRET;
```

### Password Handling
```javascript
const bcrypt = require('bcrypt');

// Hash passwords
const hashPassword = async (password) => {
  const saltRounds = 12;
  return await bcrypt.hash(password, saltRounds);
};

// Verify passwords
const verifyPassword = async (password, hash) => {
  return await bcrypt.compare(password, hash);
};
```

### JWT Security
```javascript
const jwt = require('jsonwebtoken');

// Secure JWT creation
const createToken = (payload) => {
  return jwt.sign(payload, process.env.JWT_SECRET, {
    expiresIn: '15m',
    issuer: 'your-app',
    audience: 'your-app-users'
  });
};

// Secure JWT verification
const verifyToken = (token) => {
  return jwt.verify(token, process.env.JWT_SECRET, {
    issuer: 'your-app',
    audience: 'your-app-users'
  });
};
```

### CORS Configuration
```javascript
const cors = require('cors');

// Secure CORS setup
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS.split(','),
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
```

### Rate Limiting
```javascript
const rateLimit = require('express-rate-limit');

// Apply rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.'
});

app.use('/api/', limiter);
```

## Security Headers

Implement security headers to protect against common attacks:

```javascript
const helmet = require('helmet');

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));
```

## File Upload Security

```javascript
const multer = require('multer');
const path = require('path');

// Secure file upload configuration
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    // Generate secure filename
    const uniqueName = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, uniqueName + path.extname(file.originalname));
  }
});

const fileFilter = (req, file, cb) => {
  // Allow only specific file types
  const allowedTypes = /jpeg|jpg|png|pdf|doc|docx/;
  const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
  const mimetype = allowedTypes.test(file.mimetype);
  
  if (mimetype && extname) {
    return cb(null, true);
  } else {
    cb(new Error('Invalid file type'));
  }
};

const upload = multer({
  storage,
  fileFilter,
  limits: { fileSize: 5 * 1024 * 1024 } // 5MB limit
});
```

## Database Security

### Connection Security
```javascript
// Secure database connection
const sequelize = new Sequelize(process.env.DB_NAME, process.env.DB_USER, process.env.DB_PASSWORD, {
  host: process.env.DB_HOST,
  dialect: 'mysql',
  dialectOptions: {
    ssl: {
      require: true,
      rejectUnauthorized: false
    }
  },
  logging: process.env.NODE_ENV === 'production' ? false : console.log
});
```

### Query Security
```javascript
// ❌ Vulnerable to SQL injection
const users = await sequelize.query(`SELECT * FROM users WHERE name = '${req.body.name}'`);

// ✅ Secure - Use parameterized queries
const users = await sequelize.query('SELECT * FROM users WHERE name = ?', {
  replacements: [req.body.name],
  type: QueryTypes.SELECT
});

// ✅ Even better - Use ORM methods
const users = await User.findAll({
  where: { name: req.body.name }
});
```

## Authentication Security Patterns

### Secure Login
```javascript
const login = async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Rate limiting check
    if (await isRateLimited(req.ip)) {
      return sendError(res, 'Too many login attempts', 429);
    }
    
    // Find user
    const user = await User.findOne({ where: { email } });
    if (!user) {
      // Don't reveal if user exists
      return sendError(res, 'Invalid credentials', 401);
    }
    
    // Verify password
    const isValid = await bcrypt.compare(password, user.password);
    if (!isValid) {
      await logFailedAttempt(req.ip, email);
      return sendError(res, 'Invalid credentials', 401);
    }
    
    // Check if account is active
    if (!user.isActive) {
      return sendError(res, 'Account disabled', 403);
    }
    
    // Generate tokens
    const accessToken = createAccessToken(user);
    const refreshToken = createRefreshToken(user);
    
    // Log successful login
    await logSuccessfulLogin(user.id, req.ip);
    
    sendSuccess(res, { accessToken, refreshToken });
  } catch (error) {
    sendError(res, 'Authentication failed', 500);
  }
};
```

### Password Reset Security
```javascript
const resetPassword = async (req, res) => {
  try {
    const { email } = req.body;
    const user = await User.findOne({ where: { email } });
    
    if (user) {
      // Generate secure token
      const resetToken = crypto.randomBytes(32).toString('hex');
      const hashedToken = crypto.createHash('sha256').update(resetToken).digest('hex');
      
      // Set token expiration (1 hour)
      const tokenExpiry = new Date(Date.now() + 60 * 60 * 1000);
      
      await user.update({
        resetToken: hashedToken,
        resetTokenExpiry: tokenExpiry
      });
      
      // Send email with reset link
      await sendResetEmail(user.email, resetToken);
    }
    
    // Always return success to prevent email enumeration
    sendSuccess(res, 'If that email is in our system, we have sent a password reset link to it.');
  } catch (error) {
    sendError(res, 'Password reset failed', 500);
  }
};
```

## Security Testing

### Automated Security Scanning
```bash
# Check for known vulnerabilities
npm audit

# Check for security issues in dependencies
npm audit fix

# Use security-focused linting
npm install --save-dev eslint-plugin-security
```

### Manual Security Review Checklist
- [ ] Input validation on all endpoints
- [ ] Authentication required for sensitive operations
- [ ] Authorization checks for data access
- [ ] Sensitive data not exposed in logs or responses
- [ ] Error messages don't reveal system information
- [ ] Rate limiting implemented for critical endpoints
- [ ] CORS properly configured
- [ ] Security headers implemented
- [ ] Dependencies are up to date
- [ ] No hardcoded secrets or keys

## Security Monitoring

### Logging Security Events
```javascript
const securityLogger = require('./utils/securityLogger');

// Log security events
const logSecurityEvent = (event, details) => {
  securityLogger.warn({
    event,
    timestamp: new Date().toISOString(),
    ip: details.ip,
    userId: details.userId,
    details: details.data
  });
};

// Monitor for suspicious activity
const monitorSuspiciousActivity = (req, res, next) => {
  const userAgent = req.get('User-Agent');
  const ip = req.ip;
  
  // Check for suspicious patterns
  if (isSuspiciousUserAgent(userAgent)) {
    logSecurityEvent('suspicious_user_agent', { ip, userAgent });
  }
  
  next();
};
```

This skill provides comprehensive security analysis capabilities to help identify and prevent security vulnerabilities in your codebase.