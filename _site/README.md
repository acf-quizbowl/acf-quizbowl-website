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
    $ rbenv install -l # List latest stable versions
    $ rbenv install YOUR_CHOSEN_VERSION # Install the version of your choice from the list produced by the previous command
    ```

  * Windows:

    ```{bash}
    $ rbenv install head # Install the latest version
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
  $ gem install jekyll
  ```

* Install [Bundler](https://bundler.io/).

  ```{bash}
  $ gem install bundler
  ```

### Run Locally

* Clone this repository.
* Enter the repository folder.
* Install all the Gems in the `Gemfile`:

  ```{bash}
  $ bundle install
  ```

* Run locally:

  ```{bash}
  $ bundle exec jekyll serve
  ```

## Contributing

[Create an issue](https://github.com/acf-quizbowl/acf-quizbowl.github.io/issues/new/choose) to suggest a new feature/page or discuss errors on the website.

Please [fork this repository](https://github.com/acf-quizbowl/acf-quizbowl.github.io/fork) and then [create a PR](https://github.com/acf-quizbowl/acf-quizbowl.github.io/compare) to add more features. For more info, see [GitHub's documentation](https://docs.github.com/en/get-started/quickstart/fork-a-repo).
