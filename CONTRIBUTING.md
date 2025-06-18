# Contributing to TDS Virtual TA

Thank you for considering contributing to the TDS Virtual TA project! We welcome contributions from the community to improve this tool for the IIT Madras Online Degree Program’s Tools in Data Science course.

## How to Contribute

1. **Fork the Repository**:

   - Fork [dopeforce/tds-virtual-ta](https://github.com/dopeforce/tds-virtual-ta) to your GitHub account.

2. **Clone Your Fork**:

   ```bash
   git clone https://github.com/your-username/tds-virtual-ta.git
   cd tds-virtual-ta
   ```

3. **Create a Branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Changes**:

   - Follow the project structure and coding style (PEP 8).
   - Update tests in `tests/` if adding new functionality.
   - Ensure scripts align with the existing data pipeline (`res/`).

5. **Test Your Changes**:

   ```bash
   python -m pytest tests/
   ```

6. **Commit Changes**:

   - Use clear, descriptive commit messages.

   ```bash
   git commit -m "Add feature: your feature description"
   ```

7. **Push to Your Fork**:

   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request**:
   - Submit a PR to the `main` branch of `dopeforce/tds-virtual-ta`.
   - Fill out the PR template with details of your changes.

## Guidelines

- **Code Style**: Adhere to PEP 8. Use `flake8` for linting:
  ```bash
  pip install flake8
  flake8 .
  ```
- **Tests**: Add or update tests in `tests/` for new features or bug fixes.
- **Documentation**: Update `README.md` or script comments for any changes.
- **Scope**: Focus on features or fixes relevant to the Virtual TA (data ingestion, API, question answering).
- **Respect the License**: Ensure contributions comply with the MIT License.
