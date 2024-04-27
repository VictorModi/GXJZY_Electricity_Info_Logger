# GXJZY Electricity Info Logger

## Description
GXJZY Electricity Info Logger is a Python script project designed to help users retrieve and store electricity information from the website of Guangxi Transport Vocational and Technical College (or GXJZY) into MySQL. This enables users to monitor changes in electricity data conveniently.

## Features
- **Website Information Retrieval:** Implements functionality to fetch electricity information from the GXJZY website using Python scripts, ensuring users can access the latest electricity data.
  
- **Storage in MySQL:** Electricity information is stored in a MySQL database, allowing users easy access to historical electricity data for analysis and comparison.

- **View Historical Electricity Information:** Provides functionality to view historical electricity information via Web API, enabling users to review past electricity data records easily.

- **CSV Record Retrieval:** Supports direct retrieval of electricity records in CSV format through API, enabling users to import data into other applications for processing or analysis conveniently.

- **Automatic Student Account Re-login:** Implements automatic re-login of student accounts, ensuring continuous retrieval of electricity information for users and enhancing convenience and stability of use.

## Usage
1. Install Python environment and ensure relevant dependencies are installed.
2. Fill in the appropriate website login information and MySQL connection information in the configuration file.
3. Run the script to begin retrieving electricity information and storing it in the MySQL database.

## Installation
Clone the repository:

```bash
git clone -b mysql https://github.com/VictorModi/GXJZY_Electricity_Info_Logger.git
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configuration:

Edit the `config-template.py` file and provide your website login credentials and MySQL connection details. After configuration, rename the file to `config.py`.

## License

[RemoChan Revolution Protocol 0x0 Version](https://github.com/VictorModi/GXJZY_Electricity_Info_Logger/blob/master/LICENSE)
## Contributing

Contributions are welcome. Please fork the repository, make your changes, and submit a pull request.

## Credits
This project is maintained by [Victor Modi](https://github.com/VictorModi)

## Disclaimer
This project is developed independently and is not officially affiliated with GXJZY. Users should use it responsibly and in compliance with all relevant laws and regulations. The developers do not take any responsibility for misuse of this project.
