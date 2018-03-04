# Hiking Catalog
Hiking catalog was a project I did as student enrolled in [Udacity's Fullstack Nano Degree program](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).

## About
The Hiking Catalog is a RESTful web application that provides a list of hiking trails from a variety of locations. This application uses the Python framework Flask along with implementing third-party OAuth authentication and user registration. If the user is authenticated through Google or Facebook they will have the ability to create new hiking trails and edit or delete their posts.

## Resources Used
[Udacity's Restaurant App](https://www.udacity.com/course/full-stack-foundations--ud088) - followed as learning resource

[Images](https://unsplash.com)

[Icons](http://fontawesome.io)

## Files
* src/
  *static/ - holds images and common.css file that olds the styles
  *template/ - holds are the html templates for the various sections of the page - both public side and private side.
  
## Dependencies
- [Vagrant](https://www.vagrantup.com/)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
- [Udacity Vagrantfile](https://github.com/udacity/fullstack-nanodegree-vm)

## Installation - Running the Code
* Install Vagrant and Virtual Box -> both linked above.
* Clone the Udacity Vagrantfile 
* Go to the directory you save the Vagrant vagrant file
* Start up Vagrant:
```
vagrant up
```
* Log on to the Vagrant VM:
```
vagrant ssh
```
* Navigate to /vagrant
* Install requests with:
```
sudo pip install requests
```
* cd to the src/ folder in this repo
* Run the following commands to start and populate the database:
```
python database_setup.py
python loadhikingtrails.py
```
* Run application:
```
python webserver.py
```
* Access the application locally by going to the url http://localhost:5000


  
