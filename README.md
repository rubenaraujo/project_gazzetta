# Project Gazzetta

This project scrapes and downloads high-resolution covers and thumbnails from the website [capasjornais.pt](https://capasjornais.pt/), organizing them by category. It is designed to run automatically via GitHub Actions, committing new images to the repository.

## Features
- Scrapes covers and thumbnails for several categories:
  - Jornais Nacionais
  - Revistas
  - Jornais Desportivos
  - Revistas Tecnologia
  - Revistas Carros
  - Revistas Moda
- Downloads both high-resolution covers and thumbnails
- Organizes images into folders by category
- Skips downloading images that haven't changed
- Commits and pushes new/updated images automatically via workflow

## Usage

### Local Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the scrapper:
   ```bash
   python covers_scrapper.py
   ```
3. Images will be saved in the `images/covers/<category>` and `images/thumbnails/<category>` directories.

### GitHub Actions
The workflow `.github/workflows/scrapper_workflow.yml` runs the scrapper automatically on a schedule and commits new images to the repository.

## Project Structure
- `covers_scrapper.py`: Main script for scraping and downloading images
- `requirements.txt`: Python dependencies
- `images/`: Output directory for downloaded images
- `.github/workflows/scrapper_workflow.yml`: GitHub Actions workflow for automation

## Requirements
- Python 3.x
- See `requirements.txt` for required packages

## Notes
- Uses a proxy to bypass CORS restrictions when fetching images
- Only downloads images if they are new or updated
- Make sure your GitHub workflow has permission to push to the repository

## License
MIT

## Credits & Usage

All images scraped and downloaded by this project are owned by the original website, [capasjornais.pt](https://capasjornais.pt/). This project is intended for personal use only and does not claim ownership of any images. Please respect the rights of the original content owners.
