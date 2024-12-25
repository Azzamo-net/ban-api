# Azzamo Banlist API

Azzamo Banlist API is a FastAPI-based service for managing a list of blocked public keys, IP addresses, and blacklisted words. It provides endpoints for adding, removing, and querying these entities, with support for optional ban reasons.

## Features

- **Public Key Management**: Add, remove, and check the status of public keys. Optionally, provide a reason for banning.
- **IP Address Management**: Add and remove IP addresses with optional ban reasons.
- **Word Blacklisting**: Add and remove blacklisted words or phrases.
- **Temporary Bans**: Temporarily ban public keys for a specified duration.
- **Moderator Management**: Add, remove, and list moderator keys. Moderators can manage bans and reports using their keys.
- **User Reports**: Report public keys with reasons, update report status, approve reports, and view reports.
- **Recent Activity**: View recent actions performed by moderators.
- **Data Export/Import**: Export and import all blocked data to/from text files.
- **Rate Limiting**: Apply rate limiting to all endpoints.
- **Interactive API Documentation**: Access interactive API documentation via Swagger UI.

## Public Instance

The public instance of the Azzamo Banlist API is available at [https://ban-api.azzamo.net](https://ban-api.azzamo.net).

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/azzamo-banlist-api.git
   cd azzamo-banlist-api
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**:
   Ensure your database is set up and configured in `database.py`.

5. **Run the application**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Usage

### Public Endpoints

- **Get Blocked Public Keys**: Retrieve a list of all blocked public keys.
- **Get Blocked Words**: Retrieve a list of all blacklisted words.
- **Get Blocked IPs**: Retrieve a list of all blocked IP addresses.
- **Check Public Key Status**: Check if a public key is blocked and if it is temporarily banned.
- **Create User Report**: Report a public key with a reason.
- **Get Pending Reports**: Retrieve all pending user reports.
- **Get All Reports**: Retrieve all user reports.
- **Get Successful Reports**: Retrieve all successfully reported and banned users.

### Administrative Endpoints

- **Add/Remove Blocked Public Key**: Manage blocked public keys with optional ban reasons.
- **Add/Remove Blocked IP**: Manage blocked IP addresses with optional ban reasons.
- **Add/Remove Blacklisted Word**: Manage blacklisted words or phrases.
- **Temporarily Ban/Remove Temporary Ban on Public Key**: Manage temporary bans on public keys.
- **Update/Remove Ban Reason**: Update or remove the ban reason for a public key.
- **Add/Remove/List Moderators**: Manage moderator keys. Only accessible with the admin API key.
- **Update User Report**: Update the status of a user report. Accessible with moderator or admin API keys.
- **Approve Report**: Approve a report and ban the reported user. Accessible with moderator or admin API keys.
- **Get User Reports**: Retrieve reports for a specific public key.
- **Get Recent Activity**: Retrieve recent actions performed by moderators.

### Export and Import

- **Export All Data**: Export all blocked data to text files.
- **Import All Data**: Import all blocked data from text files.

## Configuration

- **Environment Variables**: Use a `.env` file to configure environment variables.
- **Database Configuration**: Ensure your database connection is correctly set up in `database.py`.

## Development

### Code Structure

- **`main.py`**: Contains the FastAPI application and endpoint definitions.
- **`crud.py`**: Contains CRUD operations for managing public keys, IPs, words, and moderators.
- **`models.py`**: Defines the SQLAlchemy models for the database.
- **`schemas.py`**: Defines Pydantic models for request and response validation.
- **`utils.py`**: Contains utility functions for file synchronization and moderator key management.

### Debugging

Refer to the [FastAPI Debugging Guide](https://fastapi.tiangolo.com/tutorial/debugging/) for tips on debugging your FastAPI application.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please contact [michilis@azzamo.net](mailto:michilis@azzamo.net).
