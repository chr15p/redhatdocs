# redhatdocs
tool to download docs from the Red Hat documentation webste


The Red Hat docs are broken down into products and within each product are sections:

List all the products available:

./redhatdocs.py -l

List all the sections in the red-hat-enterprise-linux product:

./redhatdocs.py -p red-hat-enterprise-linux -l


download all the docs for one product:

./redhatdocs.py -p red-hat-enterprise-linux

download all the docs for one section for a  product (in this case the RHEL pacemaker add on):

./redhatdocs.py -p red-hat-enterprise-linux -l clustering
