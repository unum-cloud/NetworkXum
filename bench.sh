# PostgreSQL
brew install postgresql &&
    brew services start postgresql

# MySQL
# mysqld_safe --skip-grant-tables &
# mysql
# UPDATE mysql.user SET authentication_string='temptemp' WHERE User='root';
# FLUSH PRIVILEGES;
# exit;
brew install mysql &&
    brew services start mysql

# MongoDB
# mongod --dbpath=/Users/av/DBs/mongo/ --directoryperdb --wiredTigerCacheSizeGB=2 --wiredTigerDirectoryForIndexes &!
brew tap mongodb/brew &&
    brew install mongodb-community@4.2 &&
    brew services start mongodb/brew/mongodb-community

# Neo4J
brew cask install homebrew/cask-versions/adoptopenjdk8 &&
    brew install neo4j &&
    brew services start neo4j

# Redis
brew install redis &&
    brew services start redis

# Memcached
brew install memcached &&
    brew services start memcached

# ElasticSearch
# elasticsearch &!
brew install elasticsearch &&
    brew services start elasticsearch

~/miniconda3/bin/python setup.py install
~/miniconda3/bin/python BenchGraphs/main.py
~/miniconda3/bin/python BenchDocs/main.py
