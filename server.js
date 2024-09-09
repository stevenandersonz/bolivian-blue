const express = require("express");
const sqlite3 = require("sqlite3").verbose();

const app = express();
const PORT = process.env.PORT || 3000;

const db = new sqlite3.Database("./prices.db", sqlite3.OPEN_READONLY, (err) => {
  if (err) {
    console.error("Error connecting to the database:", err.message);
  } else {
    console.log("Connected to the SQLite database.");
  }
});

app.get("/", async (req, res) => {
  let sell = await new Promise((resolve, reject) => {
    db.get(
      "SELECT * FROM USDT2BS ORDER BY date DESC LIMIT 1",
      [],
      (err, row) => {
        if (err) {
          reject("error getting sell prices");
        }
        resolve(row);
      }
    );
  });

  let buy = await new Promise((resolve, reject) => {
    db.get("SELECT * FROM BS2USDT BY date DESC LIMIT 1", [], (err, row) => {
      if (err) {
        reject("error getting buy prices");
      }
      resolve(row);
    });
  });
  console.log(sell);
  console.log(buy);

  // Generate HTML content dynamically
  let htmlContent = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Boliviano Blue</title>
    </head>
    <body>
        <h1> Bolivian Blue </h1>
        <h2>USDT -> BO: ${sell.price}</h2>
        <h2>BO -> USDT: ${buy.price}</h2>
    </body>
    </html>
    `;

  res.send(htmlContent);
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
