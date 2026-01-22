# 🚀 AI Employee System Setup Guide

Step-by-step instructions to set up your AI Employee system.

## 📋 Prerequisites

Before starting the setup, ensure you have:

- **Python 3.13** or higher
- **UV package manager** (recommended) or pip
- **Google Cloud Account** with Gmail API access
- **Windows/Mac/Linux** operating system
- **Administrator access** for installing packages

## 📥 Installation Steps

### Step 1: Clone or Download the Repository

```bash
# If using git
git clone <repository-url>
cd ai-employee-system

# Or download and extract the zip file to your preferred location
```

### Step 2: Install Python Dependencies

Using UV (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

### Step 3: Set Up Google API Credentials

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project or select an existing one**
3. **Enable the Gmail API:**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

4. **Create OAuth 2.0 credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Select "Desktop Application" as the application type
   - Give it a name (e.g., "AI Employee System")
   - Click "Create"

5. **Download credentials:**
   - Click the download icon next to your newly created credentials
   - Save the file as `credentials.json` in your project root directory

### Step 4: Configure Environment Variables

1. **Copy the template:**
   ```bash
   cp .env.template .env
   ```

2. **Edit the `.env` file:**
   ```bash
   # Open .env in your preferred text editor
   ```

3. **Fill in your specific information:**
   ```
   # Gmail API Configuration
   GMAIL_CLIENT_ID=your_client_id_from_credentials_json
   GMAIL_CLIENT_SECRET=your_client_secret_from_credentials_json
   GMAIL_REFRESH_TOKEN=will_be_generated_after_first_auth
   GMAIL_USER_EMAIL=your-email@gmail.com

   # File Paths
   VAULT_PATH=./AI_Employee_Vault
   DROPZONE_PATH=./AI_Employee_Dropzone

   # Business Information
   BUSINESS_NAME=E-commerce Automation
   MONTHLY_REVENUE_TARGET=4000
   APPROVAL_THRESHOLD_LOW=50
   APPROVAL_THRESHOLD_HIGH=100
   ```

### Step 5: Initialize the Obsidian Vault

The system will automatically create the vault structure when you run the orchestrator for the first time. However, you can manually create it:

```bash
# The system will create this automatically, but if you want to create manually:
mkdir -p AI_Employee_Vault/{Needs_Action,Plans,In_Progress,Pending_Approval,Approved,Rejected,Done,Logs,Inbox,Accounting,Briefings,.claude/skills}
```

### Step 6: Test the System

1. **Run the orchestrator for the first time:**
   ```bash
   python orchestrator.py
   ```

2. **On first run, you'll be prompted to authenticate with Google:**
   - A browser window will open
   - Log into your Google account
   - Grant permissions for Gmail access
   - The system will create a `token.json` file

3. **Verify the system is working:**
   - Check that all vault folders are created
   - Look for log files in the `Logs/` folder
   - Verify watchers are running

### Step 7: Configure File Dropzone (Optional)

If you want to monitor a folder for new files:

1. **Create the dropzone folder:**
   ```bash
   mkdir ./AI_Employee_Dropzone
   ```

2. **The file_watcher.py will automatically monitor this folder**

## 🔧 Configuration Options

### Custom Vault Path

To use a different vault location, modify the `VAULT_PATH` in `.env` or pass it as a command line argument:

```bash
python orchestrator.py --vault-path /path/to/your/vault
```

### Custom Polling Intervals

Adjust the polling intervals by modifying the watcher configurations:

- **File watcher:** Modify `interval` parameter in `file_watcher.py`
- **Gmail watcher:** Modify `interval` parameter in `gmail_watcher.py`
- **Health checks:** Modify schedule in `orchestrator.py`

## 🔐 Security Configuration

### Approval Thresholds

Edit these values in your `.env` file:

- `APPROVAL_THRESHOLD_LOW`: Amount for medium-risk approvals (default: 50)
- `APPROVAL_THRESHOLD_HIGH`: Amount for high-risk approvals (default: 100)

### Known Contacts

Add known contacts to bypass approval requirements by modifying the `KNOWN_CONTACTS` environment variable in `.env`.

## 🧪 Testing the System

### Test File Monitoring

1. **Place a test file in the dropzone:**
   ```bash
   echo "Test file content" > ./AI_Employee_Dropzone/test_file.txt
   ```

2. **Verify a task is created in `AI_Employee_Vault/Needs_Action/`**

### Test Email Monitoring

1. **Send yourself a test email marked as important**
2. **Check `AI_Employee_Vault/Needs_Action/` for email tasks**

## 🛠️ Troubleshooting

### Common Issues

#### Issue: "Credentials file credentials.json not found"
**Solution:** Ensure `credentials.json` exists in the project root directory with proper format from Google Cloud Console.

#### Issue: "Authentication required" or "Invalid credentials"
**Solution:** Delete `token.json` and restart the orchestrator to re-authenticate.

#### Issue: "Permission denied" for vault folders
**Solution:** Check file permissions and ensure the application has read/write access.

#### Issue: "Import errors" for required packages
**Solution:** Reinstall dependencies with `pip install -r requirements.txt` or `uv sync`.

### Verifying Setup

After setup, you should have:

- ✅ `credentials.json` in project root
- ✅ `token.json` (after first authentication)
- ✅ Complete vault folder structure
- ✅ `.env` file with your configuration
- ✅ Running orchestrator with active watchers
- ✅ Log files in the `Logs/` folder

## 🚀 Next Steps

Once setup is complete:

1. **Customize the Company_Handbook.md** with your specific business rules
2. **Adjust approval thresholds** in `security_config.py` or `.env`
3. **Test with sample tasks** to verify the workflow
4. **Set up scheduled tasks** if needed
5. **Monitor the system** for the first few days to ensure proper operation

## 📞 Support

If you encounter issues during setup:

- Check the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide
- Review log files in the `Logs/` folder
- Verify all prerequisites are met
- Ensure network connectivity for API calls