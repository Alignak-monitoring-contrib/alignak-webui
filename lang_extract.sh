# Extract message from source file
python setup.py extract_messages -o alignak_webui/res/messages.pot --mapping-file message-extraction.ini --copyright-holder "Frederic MOHIER"
# Update existing catalog
python setup.py update_catalog -l fr -i alignak_webui/res/messages.pot -o alignak_webui/res/fr_FR.po
