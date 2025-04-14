# Meetings notes

## Meeting 1.
* **DATE:** 30th January 2025
* **ASSISTANTS:** Ivan Sanchez

### Minutes
The contents of the first deliverable were discussed in this meeting. After looking at our project idea, Ivan mentioned that it needed more clarity in terms of what was written in the Wiki. The key features and purpose of the API were suggested to be revised. Moreover, Ivan mentioned that it was not clear that whether the external API was using REST/grpc. And the example given for its application should have been in the context of a Journal API. 

Apart from that, it was suggested that the whole text be rewritten because of the use of AI. 

### Action points
The action points were:
- Rewrite whole text in paragraphic format.
- Revise the content of Key Features and Purpose of the API.
- Clarify the communication being used in External API example, and add a more relevant use case.
- Overall, the text should have more clarity in it.




## Meeting 2.
* **DATE:** 18th February 2025
* **ASSISTANTS:** Ivan Sanchez

### Minutes
The professor suggested to move to MariaDB or MySQL database instead of current implementation (SQLlite). He mentioned that the Readme.md should be updated each time the implementation is updated, so everyone who does not know the context can run the application on their local PC. He suggested to keep the EditHistory module of the JournalAPI to be optional or on low priority right now. 

### Action points
- Move to MariaDB or MySQL database instead of current implementation (SQLlite)
- Readme.md should be updated each time the implementation is updated
- Keep the EditHistory module of the JournalAPI to be optional or on low priority right now




## Meeting 3.
* **DATE: 18th March 2025**
* **ASSISTANTS: Mika Oja**

### Minutes
We went over Deliverable 4 with Mika. For the Wiki Report, he pointed out that the resource table is incomplete—each endpoint should be listed as a separate resource. Also, the URLs need to be improved so that each comment link includes the entry it belongs to. He mentioned that the PUT method should fully replace the resource, not just update parts of it. Lastly, the login function seems to keep some state, which shouldn't happen in a stateless system.

For the Basic Implementation, he said the folder structure isn’t correct and includes files that shouldn’t be in the repo. Some classes in the service modules are unnecessary. There are also problems with code quality (we should run pylint and fix issues), no documentation yet, and no test coverage. Although the run instructions are fine, the implementation couldn’t be fully tested because the tests aren’t running properly yet.

In the Extras section, only authentication is done. Things like URL converters, schema validation, and caching are still missing.

### Action points
- List each endpoint separately in the resource table.
- Update comment URLs to include their parent entry.
- Change the PUT method to fully replace the resource.
- Make sure the login process is stateless.
- Fix the folder structure and remove any extra files or unnecessary classes.
- Improve code quality using pylint.
- Add documentation.
- Set up test coverage and make sure tests can run.
- Add URL converters, schema validation, and caching support.




## Meeting 4.
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*




## Midterm meeting
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*




## Final meeting
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*




