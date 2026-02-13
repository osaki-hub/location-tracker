# Google Apps Script Setup Instructions

To enable data collection to your Google Spreadsheet, follow these steps:

1.  **Create a Google Sheet**:
    *   Go to [Google Sheets](https://sheets.google.com) and create a new spreadsheet.
    *   Name it "Location Data".
    *   Add headers to the first row (A1 to H1): `Timestamp`, `Latitude`, `Longitude`, `Accuracy`, `Name`, `Phone`, `Notes`, `RawData`.

2.  **Open Script Editor**:
    *   In the spreadsheet, click **Extensions** > **Apps Script**.

3.  **Paste the Code**:
    *   **Delete EVERYTHING** currently in `Code.gs` (ensure the file is completely empty first).
    *   Copy and paste the exact code block below:

```javascript
function doPost(e) {
  // Use a lock to prevent concurrent writing issues
  var lock = LockService.getScriptLock();
  lock.tryLock(10000);

  try {
    // 1. Get the active sheet
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    
    // 2. Parse the incoming JSON data
    var data = JSON.parse(e.postData.contents);
    
    // 3. Prepare the row data
    var timestamp = new Date();
    var row = [
      timestamp,
      data.latitude,
      data.longitude,
      data.accuracy,
      data.name || "",
      data.phone || "",
      data.notes || "",
      JSON.stringify(data)
    ];
    
    // 4. Append to sheet
    sheet.appendRow(row);
    
    // 5. Return success
    return ContentService.createTextOutput(JSON.stringify({ 'status': 'success' }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({ 'status': 'error', 'message': error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}

function doGet(e) {
  return ContentService.createTextOutput("Location Tracker API is running correctly.");
}
```

4.  **Deploy as Web App**:
    *   Click the blue **Deploy** button > **New deployment**.
    *   **Select type**: Web app.
    *   **Description**: "Location Tracker API".
    *   **Execute as**: **Me** (your email).
    *   **Who has access**: **Anyone** (Anyone with the link).
        *   *Note: This is critical so the Python application can send data without OAuth flow.*
    *   Click **Deploy**.
    *   Authorize the script if prompted.

5.  **Copy the Web App URL**:
    *   Copy the URL (ends with `/exec`).
    *   Go to your local Location Tracker Admin Panel (`http://127.0.0.1:3000/admin`).
    *   Paste the URL into the "Google Apps Script URL" field.
    *   Click "Save Configuration".
