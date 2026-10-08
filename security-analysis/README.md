# Security Analysis Skill

This global skill provides comprehensive security analysis capabilities for code review, vulnerability identification, and security best practices implementation.

## What This Skill Provides

- **Security Vulnerability Detection**: Identify common security issues like SQL injection, XSS, CSRF, and more
- **Security Best Practices**: Guidelines for secure coding practices and implementation
- **Security Checklists**: Comprehensive checklists for systematic security reviews
- **Security Templates**: Ready-to-use secure middleware and validation templates
- **Threat Analysis**: Framework for understanding and mitigating security threats

## How to Use This Skill

1. **Enable Skills in Cline**: Go to Settings → Features → Enable Skills
2. **Trigger the Skill**: Ask Cline security-related questions like:
   - "Analyze this code for security vulnerabilities"
   - "How do I implement secure authentication?"
   - "What are the security best practices for file uploads?"
   - "Review this API endpoint for security issues"

3. **Use Security Templates**: Copy and customize templates from the `templates/` directory
4. **Follow Checklists**: Use the comprehensive security checklist for systematic reviews

## Skill Structure

```
.cline/skills/security-analysis/
├── SKILL.md              # Main instructions (loaded when skill is triggered)
├── README.md             # This overview document
├── docs/
│   └── security-checklist.md  # Comprehensive security review checklist
└── templates/
    └── secure-middleware-template.js  # Security middleware and utilities
```

## Key Features

### 🛡️ Vulnerability Detection
- SQL injection prevention and detection
- Cross-Site Scripting (XSS) protection
- Cross-Site Request Forgery (CSRF) prevention
- Insecure Direct Object References protection
- Sensitive data exposure prevention

### 🔐 Authentication & Authorization
- Secure password handling with bcrypt
- JWT token security best practices
- Session management security
- Role-based access control (RBAC)
- Rate limiting and brute force protection

### 📊 Security Analysis Tools
- Input validation and sanitization utilities
- Security header implementation
- CORS configuration security
- File upload security measures
- Request size limiting

### 📋 Comprehensive Checklists
- Pre-analysis setup checklist
- Input validation review
- Authentication and authorization review
- Data protection review
- Error handling and logging review
- Dependencies and supply chain security
- Network security configuration
- Business logic security review

### 🛠️ Security Templates
- Secure middleware implementation
- Password validation utilities
- Token generation and validation
- SQL injection detection
- XSS detection and prevention
- Security logging and monitoring

## Security Analysis Process

### 1. Pre-Analysis Setup
- Enable the security analysis skill
- Review codebase structure and identify critical components
- Understand the application's threat model
- Identify sensitive data flows and storage locations

### 2. Systematic Review
Use the security checklist to methodically review:
- Input validation and sanitization
- Authentication and authorization mechanisms
- Data protection (encryption in transit and at rest)
- Error handling and logging practices
- Dependencies and supply chain security
- Network security configurations

### 3. Vulnerability Assessment
- Identify common security vulnerabilities
- Check for proper input validation
- Verify authentication and authorization controls
- Review data protection measures
- Assess error handling for information leakage

### 4. Security Implementation
- Apply security templates as needed
- Implement missing security controls
- Fix identified vulnerabilities
- Update security documentation

## Integration with Development Workflow

### Code Review Process
1. **Automated Security Scanning**: Use npm audit, ESLint security plugins
2. **Manual Security Review**: Apply security checklist systematically
3. **Security Testing**: Include security tests in CI/CD pipeline
4. **Regular Security Audits**: Schedule periodic comprehensive reviews

### Security Best Practices
- Never trust user input - always validate and sanitize
- Use parameterized queries to prevent SQL injection
- Implement proper authentication and authorization
- Encrypt sensitive data in transit and at rest
- Use security headers and CORS properly
- Implement rate limiting for critical endpoints
- Log security events appropriately
- Keep dependencies up to date

## Common Security Patterns

### Secure Authentication
```javascript
// Use the security templates for secure authentication
const { hashPassword, verifyPassword, createRateLimiter } = require('./templates/secure-middleware-template');

// Apply rate limiting
app.use('/api/auth', createRateLimiter(15 * 60 * 1000, 5, 'Too many login attempts'));

// Hash passwords securely
const hashedPassword = await hashPassword(password);
```

### Input Validation
```javascript
// Use built-in validation functions
const { detectSQLInjection, detectXSS, validateEmail } = require('./templates/secure-middleware-template');

// Validate and sanitize input
if (detectSQLInjection(userInput) || detectXSS(userInput)) {
  return res.status(400).json({ error: 'Invalid input detected' });
}
```

### Security Headers
```javascript
// Apply comprehensive security headers
app.use(require('./templates/secure-middleware-template').securityHeaders);
```

## Security Monitoring

### Logging Security Events
```javascript
// Use the security logger for monitoring
const { securityLogger } = require('./templates/secure-middleware-template');
app.use(securityLogger);
```

### Incident Response
- Monitor security logs for suspicious activity
- Implement alerting for security events
- Have an incident response plan ready
- Regularly review and update security measures

## Next Steps

1. **Enable the skill** in Cline settings
2. **Review existing code** using the security checklist
3. **Implement security templates** where needed
4. **Add security testing** to your development workflow
5. **Train your team** on security best practices
6. **Schedule regular security reviews**

## Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [SANS Security Guidelines](https://www.sans.org/information-security-guidelines/)
- [CWE - Common Weakness Enumeration](https://cwe.mitre.org/)

This skill transforms Cline into a security expert, providing context-aware guidance for building secure applications and identifying potential vulnerabilities before they become security incidents.