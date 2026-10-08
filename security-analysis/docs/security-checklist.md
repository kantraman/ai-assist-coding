# Security Analysis Checklist

Use this comprehensive checklist to systematically review code for security vulnerabilities and best practices.

## Pre-Analysis Setup

- [ ] Enable security analysis skill in Cline
- [ ] Review the codebase structure and identify critical components
- [ ] Understand the application's threat model and attack surface
- [ ] Identify sensitive data flows and storage locations

## Input Validation & Sanitization

### General Input Validation
- [ ] All user inputs are validated on the server-side (never trust client-side validation)
- [ ] Input length limits are enforced to prevent buffer overflows
- [ ] Input type validation (string, number, email, etc.) is implemented
- [ ] Special characters are properly escaped or sanitized
- [ ] Regular expressions are secure and don't allow ReDoS attacks

### SQL Injection Prevention
- [ ] All database queries use parameterized statements or prepared statements
- [ ] ORM methods are used instead of raw SQL where possible
- [ ] Dynamic SQL construction is avoided or properly sanitized
- [ ] Database error messages don't expose sensitive information

### XSS Prevention
- [ ] All user input is properly escaped before being output to HTML
- [ ] Content Security Policy (CSP) headers are implemented
- [ ] User-generated content is sanitized appropriately
- [ ] JavaScript execution context is properly isolated

### File Upload Security
- [ ] File type validation includes both MIME type and file extension checks
- [ ] File size limits are enforced
- [ ] Uploaded files are stored outside the web root
- [ ] File names are sanitized and made unique
- [ ] Executable files are blocked or properly sandboxed

## Authentication & Authorization

### Password Security
- [ ] Passwords are hashed using strong algorithms (bcrypt, scrypt, Argon2)
- [ ] Password hashing uses appropriate salt and cost factors
- [ ] Password strength requirements are enforced
- [ ] Password reset functionality is secure and doesn't reveal user existence

### Session Management
- [ ] Session tokens are cryptographically secure and unpredictable
- [ ] Session expiration is implemented with appropriate timeouts
- [ ] Session invalidation occurs on logout
- [ ] Session fixation attacks are prevented
- [ ] Concurrent session limits are enforced

### JWT Security
- [ ] JWT tokens have appropriate expiration times
- [ ] JWT secrets are strong and stored securely
- [ ] JWT tokens are signed and optionally encrypted
- [ ] Token refresh mechanisms are implemented securely
- [ ] JWT tokens don't contain sensitive information

### Role-Based Access Control (RBAC)
- [ ] All endpoints require appropriate authentication
- [ ] Authorization checks are performed for every sensitive operation
- [ ] Privilege escalation is prevented
- [ ] Access control lists are properly maintained
- [ ] Administrative functions have additional security measures

## Data Protection

### Encryption in Transit
- [ ] HTTPS/TLS is enforced for all communications
- [ ] SSL/TLS certificates are valid and properly configured
- [ ] Weak cipher suites are disabled
- [ ] Certificate pinning is implemented where appropriate

### Encryption at Rest
- [ ] Sensitive data in databases is encrypted
- [ ] Encryption keys are managed securely
- [ ] Key rotation policies are in place
- [ ] Backup encryption is implemented

### Sensitive Data Handling
- [ ] Sensitive data is not logged or cached inappropriately
- [ ] Data minimization principles are followed
- [ ] Data retention policies are enforced
- [ ] Secure data deletion procedures are implemented

## Error Handling & Logging

### Error Messages
- [ ] Error messages don't expose system internals or sensitive data
- [ ] Stack traces are not shown to end users
- [ ] Generic error messages are used for authentication failures
- [ ] Debug information is only available in development environments

### Logging Security
- [ ] Security events are logged appropriately
- [ ] Log files don't contain sensitive information
- [ ] Log injection attacks are prevented
- [ ] Log integrity is protected
- [ ] Log access is restricted and monitored

## Dependencies & Supply Chain Security

### Dependency Management
- [ ] All dependencies are up to date with latest security patches
- [ ] Known vulnerabilities in dependencies are identified and addressed
- [ ] Only necessary packages are installed
- [ ] Dependency versions are pinned to prevent supply chain attacks

### Code Review
- [ ] Third-party code is reviewed for security issues
- [ ] Open source components are evaluated for security posture
- [ ] Supply chain security is considered for critical dependencies

## Network Security

### CORS Configuration
- [ ] CORS policies are properly configured
- [ ] Only necessary origins are allowed
- [ ] Credentials are handled securely with CORS
- [ ] Preflight requests are handled appropriately

### Rate Limiting
- [ ] Rate limiting is implemented for critical endpoints
- [ ] Brute force attacks are prevented
- [ ] API abuse is mitigated
- [ ] Rate limiting doesn't impact legitimate users

### Security Headers
- [ ] Content Security Policy (CSP) is implemented
- [ ] X-Frame-Options prevents clickjacking
- [ ] X-Content-Type-Options prevents MIME type sniffing
- [ ] Strict-Transport-Security (HSTS) is enabled
- [ ] X-XSS-Protection is configured

## Business Logic Security

### Input Validation
- [ ] Business rules are enforced server-side
- [ ] Input validation includes business logic constraints
- [ ] Edge cases are handled appropriately
- [ ] Race conditions are prevented

### Access Control
- [ ] Data access is properly restricted
- [ ] Users can only access their own data
- [ ] Administrative functions are properly protected
- [ ] Privilege boundaries are clearly defined

## Development Security

### Environment Configuration
- [ ] Sensitive configuration is not hardcoded
- [ ] Environment variables are used for secrets
- [ ] Development and production configurations are separate
- [ ] Debug modes are disabled in production

### Code Quality
- [ ] Security-focused linting rules are enabled
- [ ] Static code analysis tools are used
- [ ] Security testing is part of the CI/CD pipeline
- [ ] Security documentation is maintained

## Incident Response Preparation

### Monitoring
- [ ] Security monitoring is implemented
- [ ] Anomaly detection is configured
- [ ] Security alerts are properly configured
- [ ] Incident response procedures are documented

### Recovery
- [ ] Backup and recovery procedures are tested
- [ ] Security incident response plan is in place
- [ ] Communication procedures are defined
- [ ] Lessons learned are documented and applied

## Compliance & Standards

### Regulatory Requirements
- [ ] Relevant security standards are followed (OWASP, NIST, etc.)
- [ ] Industry-specific compliance requirements are met
- [ ] Data protection regulations are adhered to
- [ ] Security audits are conducted regularly

### Documentation
- [ ] Security architecture is documented
- [ ] Security policies are maintained
- [ ] Security procedures are documented
- [ ] Security training materials are available

## Post-Analysis Actions

- [ ] Document all identified security issues with severity ratings
- [ ] Create remediation plans for each security vulnerability
- [ ] Prioritize fixes based on risk and impact
- [ ] Implement security improvements
- [ ] Retest security fixes
- [ ] Update security documentation
- [ ] Plan regular security reviews

## Tools & Resources

### Automated Security Tools
- [ ] npm audit for dependency vulnerabilities
- [ ] ESLint with security plugins
- [ ] Snyk or similar vulnerability scanners
- [ ] OWASP ZAP for web application testing
- [ ] SonarQube for code quality analysis

### Manual Testing
- [ ] Penetration testing tools
- [ ] Security-focused code review checklists
- [ ] Threat modeling frameworks
- [ ] Security testing methodologies

This checklist provides a comprehensive framework for conducting security analysis of your codebase. Adapt it based on your specific application requirements and threat model.