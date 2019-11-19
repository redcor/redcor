
The following have been done with regard to events in this module:

1) A field for relation with cms pages in events
2) The email template for subscription of events has been overridden so that the body of the related cms page is used

To check the working,

Create a new event and assign a cms page with body to it.
And now send out the subscription mail from that event. You can notice that the body used will be that of the related cms page


Website Cms Addon

* Addon path should  must be under the python package folder where the web adddon resides

* Configuration

    # Check the proper elements to view on Home page
    # Configure root cms page (for the Menu configuration, hence the child  will be taken as the menus and sub menus on Homepage)
    # Goto CmsMenu--> set root field for homepage menu
    # Click Apply Button to save changes
    # If check the Home Menu will show the Menu container on Home page
    # The Image Grid will be shown when you check the Image grid on form
    # Search bar and Blog News will shown when you check the appropriate boxes
    # The templates can be reused as it is named website.xxx , so will belongs under website addon
    # The depend addons can be reuse each with template names as calling by t-call



Testing!
