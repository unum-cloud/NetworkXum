# brew install postgresql
brew services start postgresql
# brew install mysql
# mysqld_safe --skip-grant-tables &
# mysql
# UPDATE mysql.user SET authentication_string='temptemp' WHERE User='root';
# FLUSH PRIVILEGES;
# exit;
brew services start mysql

# brew cask install homebrew/cask-versions/adoptopenjdk8
# brew install neo4j
brew services start neo4j

# brew tap mongodb/brew
# brew install mongodb-community@4.2
# mongod --dbpath /usr/local/var/mongodb --directoryperdb --wiredTigerDirectoryForIndexes
brew services start mongodb/brew/mongodb-community

# brew install redis
brew services start redis
# brew install memcached
brew services start memcached

brew services list
