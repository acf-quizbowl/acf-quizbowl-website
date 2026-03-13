# [acf-quizbowl.com](https://acf-quizbowl.com/)

This is the repository for the official ACF website. It is open-source, so any ACF member can contribute.

The static website is built using Jekyll, a Ruby Gem.

## Setup

### Ruby

* Install [`rbenv`](https://github.com/rbenv/rbenv) to manage Ruby versions on your device. You can also use [`chruby`](https://github.com/postmodern/chruby), but `rbenv` is recommended.
  * If you have a Mac or Linux machine, use the default `rbenv` and install [`ruby-build`](https://github.com/rbenv/ruby-build) as well.
  * If you have a Windows machine, use [`rbenv-for-windows`](https://github.com/RubyMetric/rbenv-for-windows).
* Once `rbenv` is set up, install the latest version of Ruby (as of September 2024, the website runs on Ruby 3.4.5).
  * Mac / Linux:

    ```{bash}
    rbenv install -l # List latest stable versions
    rbenv install YOUR_CHOSEN_VERSION # Install the version of your choice from the list produced by the previous command
    ```

  * Windows:

    ```{bash}
    rbenv install head # Install the latest version
    ```

* Add Ruby and Gems to your path:
  * Mac / Linux:
    * Add the following to your `.bashrc` or `.zshrc` file:

      ```{bash}
      export GEM_HOME="$(ruby -e 'puts Gem.user_dir')"
      export PATH="$PATH:$GEM_HOME/bin"
      ```

  * Windows:
    * Add the following to your `$profile` (use `> echo $profile` in PowerShell to find where this is, it's usually `Documents\PowerShell\Microsoft.PowerShell_profile.ps1`):

      ```
      $env:RBENV_ROOT = "C:\Ruby-on-Windows"
      & "$env:RBENV_ROOT\rbenv\bin\rbenv.ps1" init
      ```

### Jekyll

* [Install Jekyll](https://jekyllrb.com/docs/installation/):

  ```{bash}
  gem install jekyll
  ```

* Install [Bundler](https://bundler.io/).

  ```{bash}
  gem install bundler
  ```

### Run Locally

* Clone this repository.
* Enter the repository folder.
* Install all the Gems in the `Gemfile`:

  ```{bash}
  bundle install
  ```

* Run locally:

  ```{bash}
  bundle exec jekyll serve
  ```

## Updating Members

The ACF membership tables are maintained using [a Google Sheets spreadsheet](https://docs.google.com/spreadsheets/d/1Byrc19gXCmOYJajB5O-bUYJg-E8GuM6VrYcvkcnbW8Y/) as the source of truth, shared among ACF members. The data is synced to the website via a Python script that generates JSON, Excel, and updates the HTML tables.

### Workflow for Updating Members

1. **Update [the Google Sheets spreadsheet](https://docs.google.com/spreadsheets/d/1Byrc19gXCmOYJajB5O-bUYJg-E8GuM6VrYcvkcnbW8Y/)** with new/updated member data. The spreadsheet should have columns: Full Name, First Name, Last Name, Email, Status, Affiliations, Contributions, Skills, Last Activity. Affiliations and Contributions should be newline-separated in their cells.

2. **Run the sync script** to extract data from Google Sheets and update the website files:

   ```bash
   python3 scripts/sync_from_sheets.py [sheet_id] [--credentials credentials_file]
   ```

   This script:
   * Authenticates with Google Sheets using a service account.
   * Reads member data from the specified spreadsheet.
   * Generates `about/members.json` (JSON format).
   * Generates `members.xlsx` (Excel spreadsheet).
   * Updates the HTML tables in `about/members.md`.

   If no arguments are provided, it uses default values (sheet ID for ACF Master list and credentials file at `scripts/script-credentials.json`).

3. **Confirm the updates** by checking the generated files and running the Jekyll site locally to verify the changes.

### Google Service Account Setup

The script uses a Google Service Account for authentication. To set up or modify the service account:

1. **Create or access a Google Cloud Project** with the Google Sheets API enabled.

2. **Create a Service Account** in the Google Cloud Console:
   * Go to IAM & Admin > Service Accounts.
   * Create a new service account with appropriate permissions.
   * Generate a JSON key for the service account.

3. **Share the Google Sheet** with the service account email (found in the JSON key file under `client_email`).

4. **Place the JSON key file** in the repository at `scripts/script-credentials.json` (or specify a different path with `--credentials`).

5. **Install dependencies**:

   ```bash
   pip install gspread google-auth openpyxl
   ```

The service account needs read access to the Google Sheet. Ensure the sheet is shared with the service account's email address.

## Contributing

[Create an issue](https://github.com/acf-quizbowl/acf-quizbowl.github.io/issues/new/choose) to suggest a new feature/page or discuss errors on the website.

Please [fork this repository](https://github.com/acf-quizbowl/acf-quizbowl.github.io/fork) and then [create a PR](https://github.com/acf-quizbowl/acf-quizbowl.github.io/compare) to add more features. For more info, see [GitHub's documentation](https://docs.github.com/en/get-started/quickstart/fork-a-repo).
