/*
aqua data logger for testing gps
Caleb Rees Tulloss
5/9/2018

Public URL: https://script.google.com/macros/s/AKfycbxKm2AWyX6unin8LXDkbL7l1SUre2bDJNTTGUyMk9VhXmJRgMs/exec
Spreadsheet ID: ??

Dev Version URL: https://script.google.com/a/brown.edu/macros/s/AKfycbxWJQ_-PduZst5CvSVJPrT0MMP6YYtZhMKHELXx3_A/dev
*/

function doGet(e) {
  var params = e.parameters;
  // params is an object like a = {"cat":1, "dog":2}

  var containsSheet = false;

  // check if one of the parameters keys is "sheet"
  for (var k in params) {
    if (k == "sheet") {
      containsSheet = true;
      // if "sheet" is a parameter key, get the name of the target sheet
      var targetSheetName = params[k][0];
    }
  }

  // if "sheet" was not a parameter key, the default sheet is used
  if (containsSheet == false) {
    targetSheetName = "Sheet1";
  }

  // get the current spreadsheet
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  // check if the target sheet exists. if not, create it
  var targetSheet = ss.getSheetByName(targetSheetName);
  if (targetSheet == null) {
    targetSheet = ss.insertSheet(targetSheetName);
  }

  // set the target sheet as the active one
  ss.setActiveSheet(targetSheet);

  // current data
  var dataRange = targetSheet.getDataRange();
  var dataValues = dataRange.getValues();

  // dimensions of the currently data
  var numRows = dataValues.length;

  // add Timestamp column if necessary
  // the default dataRange is 1, 1, so instead of checking if the number of columns is 0,
  // we check if the number of rows is 1. if it ISN'T 1, that means we have one row
  // of headings and at least one more with a timestamp
  if (numRows == 1) {
    // if no column for timestamp yet, add one and increase the number of rows and columns
    var columnHeadings = ["Timestamp"];
  }
  else {
    // otherwise, the column headings retain their existing value
    var columnHeadings = dataValues[0];
  }

  // current number of columns
  var numColumns = columnHeadings.length;

  // add the current timestamp to a new row in the first column
  var newRow = new Array(numColumns);
  timestamp = Utilities.formatDate(new Date(), "EST", "yyyy-MM-dd HH:mm:ss");
  newRow[0] = timestamp;

  // add new columns if necessary, and add the value to the newRow
  for (var k in params) {
    // ignore "sheet"
    if (k != "sheet") {
       // value we want to add
      var val = params[k][0];

      // find the index of the column we want to access
      index = columnHeadings.indexOf(k);

      // if key is not already in the column headings
      if (index == -1) {
        // add it
        columnHeadings.push(k);
        numColumns++;
        // and find the index again
        index = columnHeadings.indexOf(k);

        // add the value to the end (we know it will be the last entry, so we need to push)
        newRow.push(val);
      }
      else {
        // add the value to the newRow
        newRow[index] = val;
      }
    }
  }

  // replace the first row with the new headings
  dataRange = targetSheet.getRange(1, 1, 1, numColumns);
  dataRange.setValues([columnHeadings]);

  // append the new data row to the sheet
  // if the entry for a given cell is null, need to change it to blank for the spreadsheet
  len = newRow.length;
  // interestingly, if an array entry is null, a for...in loop skips its index!
  // therefore, use a regular for loop instead
  for (var i = 0; i < len; i++) {
    if (newRow[i] == null) {
      newRow[i] = "";
    }
  }
  // append the row
  targetSheet.appendRow(newRow);

  return ContentService.createTextOutput("data logged successfully");
}
