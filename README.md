# Real Estate Data Scraper (Immospider)

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Flowchart](#flowchart)
5. [Support](#support)
6. [Contributing](#Contributing)
7. [License](#license)

## Overview

The Real Estate Web Scraping is a Python-project aimed at scraping real estate data from the Immoweb website using Python. The data includes information such as property details, location, price, and more.

## Prerequisites

1. Python 3.x
2. Install necessary packages: `pip install -r requirements.txt`

## Installation

1. Clone the repository to your local machine: `git clone https://github.com/Nithyaraaj21/immo-eliza-scraping-FireFlies`
2. Ensure you have Python installed (version 3.6 or higher).
3. Install the required libraries by running:
    ```
    pip install -r requirements.txt
    ```

## Usage
1. Open a terminal or command prompt.
2. Navigate to the directory where the script is located.
3. Run the script:
 ```
   python main.py

 ```
4. The script will start scraping real estate data from immoweb.be and save it into a CSV file named `all_data.csv` in the same directory.
5. 
## Flowchart

Start
|
v
Initialize or generate Spider
|
v
Generate URLs
|
v
Send Requests to URLs
|
v
Parse Response (URLs)
|
v
Loop through URLs:
|
v
Send Request to Listing
|
v
Parse Response (Listing)
|
v
Extract Property Details
|
v
Convert to DataFrame (df)
|
v
Append DataFrame to CSV File
|
v
End


## Support
If you encounter any issues or have any questions, please feel free to open an issue in this repository.

## Contributing

Contributions are welcome!

## License

The Wikipedia Scraper project is licensed under the [MIT License](./LICENSE.md).
