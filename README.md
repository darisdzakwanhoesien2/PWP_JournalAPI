# PWP SPRING 2025
# PROJECT NAME
# Group information
* Student 1. Name and email
* Student 2. Name and email
* Student 3. Name and email
* Student 4. Name and email


__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint, instructions on how to setup and run the client, instructions on how to setup and run the axiliary service and instructions on how to deploy the api in a production environment__

## API Overview

The Web API to be developed offers functionalities to structure non-real-time conversations among users about topics of interest. Messages are grouped in Threads, which are further grouped in Topics. The API provides an interface to access and manage these messages, supporting operations such as creating, reading, updating, and deleting users, entries, comments, and edit histories. This API is envisioned as part of a larger online learning environment system, responsible for discussion forum features that can be integrated into other components.

## Main Concepts and Relations

The main concepts of the API include Users, Entries, Comments, and Edit Histories. Users can register, update their profiles, and delete their accounts. Entries represent messages or posts created by users, which can be updated or deleted. Comments are associated with entries and can also be managed similarly. Edit Histories track changes made to entries. The relations among these concepts are represented in the state diagram included in the project documentation, illustrating the RESTful resource interactions and links.

## API Uses

The API supports both human-usable clients and machine-to-machine services. For example, a web client can allow users to interact with discussion threads, while automated services can use the API to aggregate or moderate content. The API exposes endpoints for managing users, entries, comments, and edit histories, enabling diverse clients to integrate discussion forum functionalities into their applications.

## Related Work

The API resembles typical RESTful CRUD APIs used in discussion forums and social platforms. It is classified as a hypermedia-driven REST API, providing links to related resources in responses. Similar APIs include popular forum software APIs and social media platform APIs. Example clients include web frontends and mobile applications that interact with the API to provide user interfaces for discussions and content management.
