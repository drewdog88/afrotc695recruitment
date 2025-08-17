# PowerShell Improvements for AFROTC 695 Project

## 🚀 **What's Been Fixed**

### **PowerShell 7 Installation**
- ✅ Installed PowerShell 7.5.2 (latest version)
- ✅ Better compatibility with modern tools
- ✅ Improved error handling and syntax support

### **Git Credential Management**
- ✅ Configured Windows Credential Manager
- ✅ No more credential prompts for git operations
- ✅ Better integration with GitHub

## 📋 **How to Use**

### **Option 1: Set PowerShell 7 as Default in Cursor**
1. Open Cursor Settings (Ctrl+,)
2. Search for: `terminal.integrated.shell.windows`
3. Set it to: `C:\Program Files\PowerShell\7\pwsh.exe`
4. Restart Cursor

### **Option 2: Use PowerShell 7 Manually**
```powershell
# Run PowerShell 7 directly
& "C:\Program Files\PowerShell\7\pwsh.exe"

# Or use the alias
Use-PS7
```

### **Option 3: Load Development Aliases**
```powershell
# Load the aliases and functions
. .\setup_powershell_aliases.ps1
```

## 🛠️ **Available Commands**

### **Git Shortcuts**
- `gs` - git status
- `ga` - git add
- `gc` - git commit
- `gp` - git push
- `gl` - git log

### **Helper Functions**
- `Use-PS7` - Switch to PowerShell 7
- `Test-GitRepo` - Check git repository status
- `Clear-TempFiles` - Clean up temporary files
- `Test-PythonEnv` - Check Python environment
- `git-quick-commit` - Add all and commit with message

## 🔧 **Troubleshooting**

### **If git still asks for credentials:**
```powershell
git config --global credential.helper manager-core
```

### **If PowerShell 7 isn't found:**
```powershell
# Add to PATH manually
$env:PATH += ";C:\Program Files\PowerShell\7"
```

### **If you get execution policy errors:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📝 **Recommended Workflow**

1. **Use PowerShell 7** for all development work
2. **Load aliases** at the start of each session
3. **Use shortcuts** like `gs`, `ga`, `gc` for faster git operations
4. **Test commands** with `Test-GitRepo` before committing

## 🎯 **Benefits**

- ✅ **No more credential prompts**
- ✅ **Better error messages**
- ✅ **Faster git operations**
- ✅ **Modern PowerShell features**
- ✅ **Cross-platform compatibility**
- ✅ **Improved debugging**

## 📚 **Additional Resources**

- [PowerShell 7 Documentation](https://docs.microsoft.com/en-us/powershell/)
- [Git with PowerShell](https://git-scm.com/book/en/v2/Appendix-A%3A-Git-in-Other-Environments-Git-in-PowerShell)
- [Cursor Terminal Settings](https://code.visualstudio.com/docs/editor/integrated-terminal)
