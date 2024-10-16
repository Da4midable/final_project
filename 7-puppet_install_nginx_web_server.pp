# Define a class for Nginx configuration
class nginx {

  # Package resource to install nginx
  package { 'nginx':
    ensure => present,
  }

  # Service resource to manage the Nginx service
  service { 'nginx':
    ensure => running,
    enable => true,
  }

  # File resource for the default server configuration
  file { '/etc/nginx/sites-available/default':
    ensure => present,
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    content => <<EOF
server {
  listen 80;
  server_name localhost;

  # Serve content from `/var/www/html`
  location / {
    root   /var/www/html;
    index  index.html index.htm;
  }

  # Redirect for `/redirect_me` with clear message
  location /redirect_me {
    return 301 https://www.youtube.com/watch?v=QH2-TGUlwu4;
  }
}
EOF
  }

  # Ensure the default site is enabled using a symlink
  file { '/etc/nginx/sites-enabled/default':
    ensure => link,
    target => '/etc/nginx/sites-available/default',
  }

  # Ensure the www directory exists for web content
  file { '/var/www/html':
    ensure => directory,
    owner   => 'www-data',
    group   => 'www-data',
    mode    => '0755',
  }

  # Create the index.html file with "Hello World!" content
  file { '/var/www/html/index.html':
    ensure => present,
    owner   => 'www-data',
    group   => 'www-data',
    mode    => '0644',
    content => "<!DOCTYPE html><html><head><title>Hello World!</title></head><body><h1>Hello World!</h1></body></html>",
  }

  # Reload Nginx service after configuration changes (optional)
  notify { '/etc/nginx/sites-available/default':
    subscribe => Package['nginx'],
  }
}

# Apply the Nginx class
include nginx
