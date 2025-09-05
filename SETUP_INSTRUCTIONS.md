# 🚀 Trading Signals API - Complete Setup Instructions

## 📁 **File Structure**
Make sure all these files are in the same directory:
```
C:\Users\abwal\Desktop\Cursor project\
├── server.py              # Main server code
├── test_server.py         # Test script
├── start_server.bat       # Windows batch startup
├── start_server.ps1       # PowerShell startup
├── requirements.txt       # Package dependencies
└── SETUP_INSTRUCTIONS.md  # This file
```

## 🎯 **Step-by-Step Setup**

### **Step 1: Open Command Prompt as Administrator**
- Press `Windows + X`
- Select "Windows PowerShell (Admin)" or "Command Prompt (Admin)"
- Click "Yes" when prompted by User Account Control

### **Step 2: Navigate to Project Directory**
```cmd
cd C:\Users\abwal\Desktop\Cursor project
```

### **Step 3: Install Python Dependencies**
```cmd
py -m pip install -r requirements.txt
```

### **Step 4: Start the Server**
Choose one of these methods:

#### **Method A: Direct Python Command**
```cmd
py server.py
```

#### **Method B: Using Batch File**
```cmd
start_server.bat
```

#### **Method C: Using PowerShell Script**
```powershell
.\start_server.ps1
```

## ✅ **Verification Steps**

### **Step 5: Test Server Connection**
Open a **new** Command Prompt window and run:
```cmd
cd C:\Users\abwal\Desktop\Cursor project
py test_server.py
```

**Expected Output:**
```
Testing server connection...
✅ Server is running! Status: 200
Response: {'status': 'healthy', 'timestamp': '...'}
```

### **Step 6: Test API Endpoints**
Open your web browser and visit:
- **Health Check**: http://localhost:8002/api/health
- **API Root**: http://localhost:8002/

## 🔧 **Troubleshooting**

### **If PowerShell Script Won't Run:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **If Python Not Found:**
```cmd
py --version
```
If this fails, install Python from Microsoft Store or python.org

### **If Port 8002 is Busy:**
The server will show an error. Close any other applications using port 8002.

## 🎉 **Success Indicators**

✅ **Server starts without errors**
✅ **Test script shows "Server is running! Status: 200"**
✅ **Browser can access http://localhost:8002/api/health**
✅ **No error messages in the server console**

## 🚀 **Next Steps**

Once the server is running successfully:
1. **Test API endpoints** using the test script
2. **Start monitoring symbols** via API calls
3. **Create a frontend** to interact with the API
4. **Deploy to production** when ready

## 📞 **Need Help?**

If you encounter any issues:
1. Check that all files are in the same directory
2. Ensure Python is installed and accessible via `py` command
3. Verify no other applications are using port 8002
4. Run the test script to verify connectivity

---
**Happy Trading! 🎯📈**
