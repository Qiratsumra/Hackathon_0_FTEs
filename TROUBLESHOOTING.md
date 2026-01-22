# 🔧 AI Employee System Troubleshooting Guide

Common issues and solutions for the AI Employee system.

## 🚨 Critical Issues

### System Won't Start

**Problem**: Orchestrator fails to start
```
python orchestrator.py
# Error occurs immediately
```

**Solutions**:
1. **Check Python version**: Ensure Python 3.13+ is installed
   ```bash
   python --version
   ```

2. **Verify dependencies**: Install missing packages
   ```bash
   pip install -r requirements.txt
   # Or
   uv sync
   ```

3. **Check file permissions**: Ensure read/write access to project directory

### Authentication Failures

**Problem**: "Credentials file credentials.json not found"
```
2026-01-22 11:44:14,778 - GmailWatcher - ERROR - Credentials file credentials.json not found
```

**Solutions**:
1. **Verify credentials.json exists** in project root directory
2. **Check file format** - ensure it has proper Google API structure
3. **Validate file permissions** - ensure readable by the application

**Problem**: "Invalid grant" or "Authentication failed"
```
google.auth.exceptions.RefreshError: ('invalid_grant', ...)
```

**Solutions**:
1. **Delete token.json** and restart orchestrator to re-authenticate
2. **Check system clock** - ensure accurate time/date
3. **Verify Google API credentials** are still valid in Cloud Console

## ⚠️ Common Issues

### File Watcher Not Detecting Files

**Problem**: Placing files in dropzone doesn't create tasks

**Solutions**:
1. **Check dropzone path**: Verify `./AI_Employee_Dropzone` exists
2. **Check supported file types**: Ensure file extension is in supported list
3. **Check file size**: Large files might be skipped (check configuration)
4. **Restart orchestrator**: Sometimes watchers need restarting

### Email Tasks Not Creating

**Problem**: Gmail watcher runs but no tasks appear

**Solutions**:
1. **Check email filter**: Verify filter in `gmail_watcher.py` matches your needs
2. **Check Gmail labels**: Ensure emails have correct labels (important, unread, etc.)
3. **Verify API quota**: Check Google Cloud Console for API usage limits
4. **Check authentication**: Ensure token is still valid

### Task Processing Stuck

**Problem**: Tasks remain in `Needs_Action/` or `In_Progress/` indefinitely

**Solutions**:
1. **Check Claude integration**: Verify Claude Code is properly configured
2. **Review logs**: Check log files for error messages
3. **Manual intervention**: Move stuck files to appropriate folders
4. **Restart orchestrator**: Sometimes a restart clears stuck processes

## 🔍 Diagnostic Commands

### Check System Status
```bash
# Check if orchestrator is running
ps aux | grep orchestrator

# Check log files
tail -f AI_Employee_Vault/Logs/orchestrator_*.log

# Check vault folder contents
ls -la AI_Employee_Vault/Needs_Action/
ls -la AI_Employee_Vault/In_Progress/
ls -la AI_Employee_Vault/Pending_Approval/
```

### Verify Configuration
```bash
# Check environment variables
python -c "import os; print('GMAIL_USER_EMAIL:', os.getenv('GMAIL_USER_EMAIL'))"

# Check vault structure
python -c "from pathlib import Path; vault = Path('./AI_Employee_Vault'); print('Exists:', vault.exists()); [print(f'{d.name}: {d.exists()}') for d in vault.iterdir() if d.is_dir()]"
```

### Test Individual Components
```bash
# Test file watcher only
python file_watcher.py

# Test Gmail watcher only (may trigger authentication)
python gmail_watcher.py

# Check security configuration
python -c "from security_config import security_config; print('Thresholds:', security_config.get_approval_thresholds())"
```

## 📁 Vault Folder Issues

### Missing Folders
**Problem**: Vault folders don't exist or are incomplete

**Solution**: System should create folders automatically, but you can create manually:
```bash
mkdir -p AI_Employee_Vault/{Needs_Action,Plans,In_Progress,Pending_Approval,Approved,Rejected,Done,Logs,Inbox,Accounting,Briefings,.claude/skills}
```

### Permission Issues
**Problem**: "Permission denied" when creating or moving files

**Solutions**:
1. **Check directory ownership** and permissions
2. **Run with appropriate privileges** if needed
3. **Verify disk space** is available

## 🌐 Network and API Issues

### Gmail API Errors
**Problem**: "Quota exceeded" or "Rate limit exceeded"

**Solutions**:
1. **Reduce polling frequency** in `gmail_watcher.py`
2. **Check Google Cloud Console** for quota usage
3. **Implement exponential backoff** (already built into system)

### Connection Timeouts
**Problem**: "Timeout" or "Connection refused" errors

**Solutions**:
1. **Check internet connectivity**
2. **Verify firewall settings** allow API calls
3. **Check proxy settings** if behind corporate firewall

## 🛡️ Security-Related Issues

### Approval Requests Not Creating
**Problem**: Actions that should require approval don't generate requests

**Solutions**:
1. **Check security_config.py** for correct threshold settings
2. **Verify contact recognition** - ensure emails are properly identified
3. **Check log files** for security validation messages

### False Positives in Security Checks
**Problem**: Known contacts or low-risk actions incorrectly flagged for approval

**Solutions**:
1. **Update known contacts list** in security configuration
2. **Adjust approval thresholds** as needed
3. **Review security rules** in security_config.py

## 📊 Performance Issues

### High Memory Usage
**Problem**: System consuming excessive memory

**Solutions**:
1. **Reduce polling frequencies**
2. **Limit concurrent operations**
3. **Monitor for memory leaks** in log files

### Slow Task Processing
**Problem**: Delays in processing tasks

**Solutions**:
1. **Check system resources** (CPU, memory, disk)
2. **Verify network connectivity** for API calls
3. **Optimize file sizes** in dropzone
4. **Review Claude Code integration** performance

## 🔁 Recovery Procedures

### After System Crash
1. **Check log files** for error details
2. **Verify vault integrity** - check for corrupted files
3. **Restart orchestrator** with `python orchestrator.py`
4. **Manually process** any stuck tasks if needed

### Lost Configuration
1. **Restore from backup** if available
2. **Re-download credentials.json** from Google Cloud Console
3. **Re-create .env file** from .env.template
4. **Re-create vault structure** if needed

### Corrupted Token
1. **Delete token.json** file
2. **Restart orchestrator** to trigger re-authentication
3. **Follow OAuth flow** again in browser

## 📞 Support Commands

### Get System Information
```bash
# Python version
python --version

# Check dependencies
pip list | grep -E "(google|gmail|oauth|asyncio|watchdog)"

# Check system resources
python -c "import psutil; print('CPU:', psutil.cpu_percent(), '%'); print('Memory:', psutil.virtual_memory().percent, '%')"
```

### Enable Debug Logging
Add debug logging temporarily by modifying the logging configuration in orchestrator.py or watcher files.

### Generate Support Bundle
```bash
# Collect recent logs
cp AI_Employee_Vault/Logs/*.log ./support_logs/
# Collect configuration
cp .env .env.backup  # Remove sensitive data before sharing!
cp mcp.json ./support_logs/
# Collect recent task files (remove sensitive content!)
```

## 🆘 When to Seek Help

Contact support when experiencing:
- Persistent authentication issues after following troubleshooting steps
- Repeated system crashes or instability
- Security-related concerns or suspicious activity
- Data corruption or loss
- Performance issues that impact business operations

**Before contacting support, prepare:**
- Error messages and timestamps
- Recent log files
- Steps to reproduce the issue
- System configuration details
- Expected vs. actual behavior