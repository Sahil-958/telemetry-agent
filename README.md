# System Diagnostic Utility

Internal tools for system environment monitoring and data synchronization.

## Setup Instructions

### 1. Requirements
Ensure you have Python 3.8+ installed.
Install the necessary modules:
```bash
pip install -r requirements.txt
```

### 2. Configuration
1.  **Environment:** Populated `.env` with the necessary endpoint token.
2.  **Diagnostics:**
    *   Run the diagnostic tool: `python net_diag.py`.
    *   Update the `.env` file with the retrieved ID.

### 3. Execution
To start the background service:
```bash
python win_svc.py
```
For silent execution in the background, use the initialization script: `sys_init.vbs`.

## Files
*   `win_svc.py`: Main service host.
*   `net_diag.py`: Network diagnostic utility.
*   `sys_init.vbs`: System initialization helper.
*   `.env`: Configuration parameters.

## Compliance
Standard corporate data handling protocols apply. Ensure all organizational consent requirements are met before deployment.
