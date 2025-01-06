# IMPORTING THE NECESSARY PACKAGES

from MailManager import mail
from decouple import config
from datetime import datetime

# CLASS : JiraMailMessage

class JiraMailMessage :

    # INITIALIZATION METHOD

    def __init__(
    
    self,
    event_type : str | None = None,
    issue_type : str | None = None,
    description : str | None = None,
    status : str | None = None,
    key : str | None = None,
    summary : str | None = None,
    priority : str | None = None,
    comment : str | None = None,
    creator_username : str | None = None,
    creator_email : str | None = None,
    commentor_username : str | None = None,
    commentor_email : str | None = None,
    assigner_username : str | None = None,
    assigner_email : str | None = None,
    assignee_username : str | None = None,
    assignee_email : str | None = None,
    new_assignee_username : str | None = None,
    new_assignee_email : str | None = None,
    resolver_username : str | None = None,
    resolver_email : str | None = None,
    closer_username : str | None = None,
    closer_email : str | None = None,
    stopper_username : str | None = None,
    stopper_email : str | None = None,
    starter_username: str | None = None,
    starter_email : str | None = None,
    *arg, **kwargs
    
    ) : 
    
        for key, value in kwargs:
          setattr(self, key, value)

        # PASSED ATTRIBUTES

        self.event_type = event_type
        self.issue_type = issue_type
        self.description = description
        self.status = status
        self.key = key
        self.summary = summary
        self.priority = priority
        self.comment = comment
        self.creator_username = creator_username
        self.creator_email = creator_email
        self.commentor_username = commentor_username
        self.commentor_email = commentor_email
        self.assigner_username = assigner_username
        self.assigner_email = assigner_email
        self.assignee_username = assignee_username
        self.assignee_email = assignee_email
        self.new_assignee_username = new_assignee_username
        self.new_assignee_email = new_assignee_email
        self.resolver_username = resolver_username
        self.resolver_email = resolver_email
        self.closer_username = closer_username
        self.closer_email = closer_email
        self.stopper_username = stopper_username
        self.stopper_email = stopper_email
        self.starter_username = starter_username
        self.starter_email = starter_email

        # BUILT ATTRIBUTES

        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.url = f"""{config("JIRA_WEB_PROTOCOL")}://{config("JIRA_INSTANCE_URL")}/browse/{self.key}"""
        self.title = f"{self.key} - {self.summary}"
        self.includeCreator = config("INCLUDE_CREATOR")

    #  SETTING UP THE SUBJECT 

        match self.event_type :
    
            case "issue_created" :
    
                self.IssueCreated = True
                self.IssueCommented = False
                self.IssueAssigned = False
                self.IssueWorkStarted = False
                self.IssueWorkStopped = False
                self.IssueResolved = False
                self.IssueClosed = False
    
            case "issue_commented" :
    
                self.IssueCreated = False
                self.IssueCommented = True
                self.IssueAssigned = False
                self.IssueWorkStarted = False
                self.IssueWorkStopped = False
                self.IssueResolved = False
                self.IssueClosed = False
    
            case "issue_assigned" :
    
                self.IssueCreated = False
                self.IssueCommented = False
                self.IssueAssigned = True
                self.IssueWorkStarted = False
                self.IssueWorkStopped = False
                self.IssueResolved = False
                self.IssueClosed = False
    
    
            case "issue_work_started" :
    
                self.IssueCreated = False
                self.IssueCommented = False
                self.IssueAssigned = False
                self.IssueWorkStarted = True
                self.IssueWorkStopped = False
                self.IssueResolved = False
                self.IssueClosed = False
    
    
            case "issue_work_stopped" :
    
                self.IssueCreated = False
                self.IssueCommented = False
                self.IssueAssigned = False
                self.IssueWorkStarted = False
                self.IssueWorkStopped = True
                self.IssueResolved = False
                self.IssueClosed = False
    
    
            case "issue_resolved" :
    
                self.IssueCreated = False
                self.IssueCommented = False
                self.IssueAssigned = False
                self.IssueWorkStarted = False
                self.IssueWorkStopped = False
                self.IssueResolved = True
                self.IssueClosed = False
    
    
            case "issue_closed" :
    
                self.IssueCreated = False
                self.IssueCommented = False
                self.IssueAssigned = False
                self.IssueWorkStarted = False
                self.IssueWorkStopped = False
                self.IssueResolved = False
                self.IssueClosed = True

            case _ :
            
                self.IssueCreated = True
                self.IssueCommented = False
                self.IssueAssigned = False
                self.IssueWorkStarted = False
                self.IssueWorkStopped = False
                self.IssueResolved = False
                self.IssueClosed = True           
                
        # USING THE METHODS BY DEFAULT ( THEY ARE DEFINED LATER IN THE CLASS )

        self.MakeContent()
        self.SendMail()

    def MakeContent(self) :

        if self.IssueCreated :
            self.assigneeSubject = f"JIRA - NEW ISSUE WAS CREATED AT {self.timestamp} FOR YOU !" 
            self.creatorSubject = f"JIRA - NEW ISSUE WAS CREATED AT {self.timestamp} BY YOU !"

        elif self.IssueCommented :
            if self.includeCreator :
               self.creatorSubject = f"JIRA - NEW COMMENT AT {self.timestamp} IN YOUR ISSUE !"
            self.assigneeSubject = f"JIRA - NEW COMMENT AT {self.timestamp} FOR YOU !"
            self.commentorSubject = f"JIRA - NEW COMMENT AT {self.timestamp} BY YOU !"

        elif self.IssueAssigned :
            if self.includeCreator :
                self.creatorSubject = f"JIRA - NEW ASSIGNMENT AT {self.timestamp} ON YOUR ISSUE !"
            self.assigneeSubject = f"JIRA - ASSIGNMENT REMOVED FROM YOU AT {self.timestamp} !"
            self.assignerSubject = f"JIRA - NEW ASSIGNMENT AT {self.timestamp} BY YOU !"
            self.newAssgineeSubject = f"JIRA - NEW ASSIGNMENT AT {self.timestamp} TO YOU !"

        elif self.IssueWorkStarted :
            if self.includeCreator :
                self.creatorSubject = f"JIRA - ISSUE CREATED BY YOU STARTED AT {self.timestamp} !"
            self.assigneeSubject = f"JIRA - ISSUE ASSIGNED TO YOU STARTED AT {self.timestamp} !"
            self.starterSubject = f"JIRA - YOU STARTED AN ISSUE AT {self.timestamp} !"

        elif self.IssueWorkStopped :
            if self.includeCreator :
                self.creatorSubject = f"JIRA - ISSUE CREATED BY YOU STOPPED AT {self.timestamp} !"
            self.assigneeSubject = f"JIRA - ISSUE ASSIGNED TO YOU STOPPED AT {self.timestamp} !"
            self.stopperSubject = f"JIRA - YOU STOPPED AN ISSUE AT {self.timestamp} !"

        elif self.IssueResolved :
            if self.includeCreator :
                self.creatorSubject = f"JIRA - ISSUE CREATED BY YOU RESOLVED AT {self.timestamp} !"
            self.assigneeSubject = f"JIRA - ISSUE ASSIGNED TO YOU RESOLVED AT {self.timestamp} !"
            self.resolverSubject = f"JIRA - YOU RESOLVED AN ISSUE AT {self.timestamp}"

        elif self.IssueClosed :
            if self.includeCreator :
                self.creatorSubject = f"JIRA - TICKET CREATED BY YOU CLOSED AT {self.timestamp} !"
            self.assigneeSubject = f"JIRA - TICKET ASSIGNED TO YOU CLOSED AT {self.timestamp} !"
            self.closerSubject = f"JIRA - YOU CLOSED AN ISSUE AT {self.timestamp} !"

        else : 
            raise ValueError

    # MAKING THE BODY OF THE MESSAGE ( MAIL )

        if self.IssueCreated :
            self.creatorBody = (f"""
                                    {self.title}
                                    ____________________________________________________

                                    Creator : {self.creator_username} ( You )
                                    Assignee : {self.assignee_username}
                                    Priority : {self.priority}
                                    Type : {self.issue_type}
                                    Status : {self.status}
                                    ____________________________________________________

                                    Description : 
                                    {self.description}
                                    ____________________________________________________

                                    URL : {self.url}

                                    Message From Jira - Notifier At {self.timestamp}
                                """)
            self.assigneeBody = (f"""
                                     {self.title}
                                    ____________________________________________________

                                    Creator : {self.creator_username} 
                                    Assignee : {self.assignee_username} ( You )
                                    Priority : {self.priority}
                                    Type : {self.issue_type}
                                    Status : {self.status}
                                    ____________________________________________________

                                    Description : 
                                    {self.description}
                                    ____________________________________________________

                                    URL : {self.url}

                                    Message From Jira - Notifier At {self.timestamp}                                   
                                """)

        elif self.IssueCommented :
            if self.includeCreator :
                self.creatorBody = (f"""
                                        {self.title}
                                        ____________________________________________________

                                        Creator : {self.creator_username} ( You )
                                        Assignee : {self.assignee_username}
                                        Commentor : {self.commentor_username}
                                        Priority : {self.priority}
                                        Type : {self.issue_type}
                                        Status : {self.status}
                                        ____________________________________________________

                                        Comment : 
                                        {self.comment}
                                        ____________________________________________________

                                        URL : {self.url}

                                        Message From Jira - Notifier At {self.timestamp}   
                                    """)
            self.assigneeBody = (f"""
                                     {self.title}
                                    ____________________________________________________

                                    Creator : {self.creator_username} 
                                    Assignee : {self.assignee_username} ( You )
                                    Commentor : {self.commentor_username}
                                    Priority : {self.priority}
                                    Type : {self.issue_type}
                                    Status : {self.status}
                                    ____________________________________________________

                                    Comment : 
                                    {self.comment}
                                    ____________________________________________________

                                    URL : {self.url}

                                    Message From Jira - Notifier At {self.timestamp}   
                                """)
            self.commentorBody = (f"""
                                     {self.title}
                                    ____________________________________________________

                                    Creator : {self.creator_username} 
                                    Assignee : {self.assignee_username}
                                    Commentor ; {self.commentor_username} ( you )
                                    Priority : {self.priority}
                                    Type : {self.issue_type}
                                    Status : {self.status}
                                    ____________________________________________________

                                    Comment : 
                                    {self.comment}
                                    ____________________________________________________

                                    URL : {self.url}

                                    Message From Jira - Notifier At {self.timestamp}   
                                """)

        elif self.IssueAssigned :
            if self.includeCreator :
                self.creatorBody = (f"""
                                       {self.title}
                                       ____________________________________________________

                                       Creator : {self.creator_username} ( You )
                                       Assigner : {self.assigner_username}
                                       Old Assignee : {self.assignee_username}
                                       New Assignee : {self.new_assignee_username}
                                       Priority : {self.priority}
                                       Type : {self.issue_type}
                                       Status : {self.status}
                                       ____________________________________________________

                                       URL : {self.url}

                                       Message From Jira - Notifier At {self.timestamp} 
                                    """)           
            self.assigneeBody = (f"""   
                                     {self.title}
                                     ____________________________________________________
 
                                     Creator : {self.creator_username}
                                     Assigner : {self.assigner_username}
                                     Old Assignee : {self.assignee_username} ( You )
                                     New Assignee : {self.new_assignee_username}
                                     Priority : {self.priority}
                                     Type : {self.issue_type}
                                     Status : {self.status}
                                     ____________________________________________________

                                     URL : {self.url}

                                     Message From Jira - Notifier At {self.timestamp} 
                                """)
            self.assignerBody = (f"""
                                     {self.title}
                                     ____________________________________________________

                                     Creator : {self.creator_username}
                                     Assigner : {self.assigner_username} (You )
                                     Old Assignee : {self.assignee_username}
                                     New Assignee : {self.new_assignee_username}
                                     Priority : {self.priority}
                                     Type : {self.issue_type}
                                     Status : {self.status}
                                     ____________________________________________________

                                     URL : {self.url}

                                     Message From Jira - Notifier At {self.timestamp} 
                                """)
            self.newAssigneeBody = (f"""    
                                        {self.title}
                                        ____________________________________________________

                                        Creator : {self.creator_username}
                                        Assigner : {self.assigner_username}
                                        Old Assignee : {self.assignee_username}
                                        New Assignee : {self.new_assignee_username} ( You )
                                        Priority : {self.priority}
                                        Type : {self.issue_type}
                                        Status : {self.status}
                                        ____________________________________________________

                                        URL : {self.url}

                                        Message From Jira - Notifier At {self.timestamp} 
                                    """)

        elif self.IssueWorkStarted :
            if self.includeCreator :
                self.creatorBody = (f"""
                                        {self.title}
                                        ____________________________________________________

                                        Creator : {self.creator_username} ( You )
                                        Assignee : {self.assignee_username}
                                        Starter : {self.starter_username}
                                        Priority : {self.priority}
                                        Type : {self.issue_type}
                                        Status : {self.status}
                                        ____________________________________________________

                                        URL : {self.url}

                                        Message From Jira - Notifier At {self.timestamp} 
                                    """)
            self.assigneeBody = (f"""
                                     {self.title}
                                    ____________________________________________________

                                    Creator : {self.creator_username} 
                                    Assignee : {self.assignee_username} ( You )
                                    Starter : {self.starter_username}
                                    Priority : {self.priority}
                                    Type : {self.issue_type}
                                    Status : {self.status}
                                    ____________________________________________________

                                    URL : {self.url}

                                    Message From Jira - Notifier At {self.timestamp}  
                                """)
            self.starterBody = (f"""
                                     {self.title}
                                    ____________________________________________________

                                    Creator : {self.creator_username} 
                                    Assignee : {self.assignee_username}
                                    Starter : {self.starter_username} ( You )
                                    Priority : {self.priority}
                                    Type : {self.issue_type}
                                    Status : {self.status}
                                    ____________________________________________________

                                    URL : {self.url}

                                    Message From Jira - Notifier At {self.timestamp} 
                                """)

        elif self.IssueWorkStopped :
            if self.includeCreator :
                self.creatorBody = (f"""
                                        {self.title}
                                        ____________________________________________________

                                        Creator : {self.creator_username} ( You )
                                        Assignee : {self.assignee_username}
                                        Stopper : {self.stopper_username}
                                        Priority : {self.priority}
                                        Type : {self.issue_type}
                                        Status : {self.status}
                                        ____________________________________________________

                                        URL : {self.url}

                                        Message From Jira - Notifier At {self.timestamp} 
                                    """)
            self.assigneeBody = (f"""
                                     {self.title}
                                    ____________________________________________________

                                    Creator : {self.creator_username} 
                                    Assignee : {self.assignee_username} ( You )
                                    Stopper : {self.stopper_username}
                                    Priority : {self.priority}
                                    Type : {self.issue_type}
                                    Status : {self.status}
                                    ____________________________________________________

                                    URL : {self.url}

                                    Message From Jira - Notifier At {self.timestamp} 
                                """)
            self.stopperBody = (f"""
                                     {self.title}
                                    ____________________________________________________

                                    Creator : {self.creator_username} 
                                    Assignee : {self.assignee_username}
                                    Stopper : {self.stopper_username} ( You )
                                    Priority : {self.priority}
                                    Type : {self.issue_type}
                                    Status : {self.status}
                                    ____________________________________________________

                                    URL : {self.url}

                                    Message From Jira - Notifier At {self.timestamp} 
                                """)

        elif self.IssueResolved :
            if self.includeCreator :
                self.creatorBody = (f"""
                                        {self.title}
                                        ____________________________________________________

                                        Creator : {self.creator_username} ( You )
                                        Assignee : {self.assignee_username}
                                        Resolver : {self.resolver_username}
                                        Priority : {self.priority}
                                        Type : {self.issue_type}
                                        Status : {self.status}
                                        ____________________________________________________

                                        URL : {self.url}

                                        Message From Jira - Notifier At {self.timestamp} 
                                    """)
            self.assigneeBody = (f"""
                                     {self.title}
                                    ____________________________________________________

                                    Creator : {self.creator_username} 
                                    Assignee : {self.assignee_username} ( You )
                                    Resolver : {self.resolver_username}
                                    Priority : {self.priority}
                                    Type : {self.issue_type}
                                    Status : {self.status}
                                    ____________________________________________________

                                    URL : {self.url}

                                    Message From Jira - Notifier At {self.timestamp} 
                                """)
            self.resolverBody = (f"""
                                     {self.title}
                                    ____________________________________________________

                                    Creator : {self.creator_username} 
                                    Assignee : {self.assignee_username}
                                    Resolver : {self.resolver_username} ( You )
                                    Priority : {self.priority}
                                    Type : {self.issue_type}
                                    Status : {self.status}
                                    ____________________________________________________

                                    URL : {self.url}

                                    Message From Jira - Notifier At {self.timestamp} 
                                """)

        elif self.IssueClosed :
            if self.includeCreator :
                self.creatorBody = (f"""
                                        {self.title}
                                        ____________________________________________________

                                        Creator : {self.creator_username} ( You )
                                        Assignee : {self.assignee_username}
                                        Closer : {self.closer_username}
                                        Priority : {self.priority}
                                        Type : {self.issue_type}
                                        Status : {self.status}
                                        ____________________________________________________

                                        URL : {self.url}

                                        Message From Jira - Notifier At {self.timestamp} 
                                    """)
            self.assigneeBody = (f"""
                                     {self.title}
                                    ____________________________________________________

                                    Creator : {self.creator_username} 
                                    Assignee : {self.assignee_username} ( You )
                                    Closer : {self.closer_username}
                                    Priority : {self.priority}
                                    Type : {self.issue_type}
                                    Status : {self.status}
                                    ____________________________________________________

                                    URL : {self.url}

                                    Message From Jira - Notifier At {self.timestamp} 
                                """)
            self.closerBody = (f"""
                                     {self.title}
                                    ____________________________________________________

                                    Creator : {self.creator_username} 
                                    Assignee : {self.assignee_username} 
                                    Closer : {self.closer_username} ( You )
                                    Priority : {self.priority}
                                    Type : {self.issue_type}
                                    Status : {self.status}
                                    ____________________________________________________

                                    URL : {self.url}

                                    Message From Jira - Notifier At {self.timestamp}
                                """)

        else :
            raise ValueError
        
    # SENDING THE MESSAGE

    def SendMail(self) :

        if self.IssueCreated :
            mail(self.creator_email,self.creatorSubject,self.creatorBody)
            mail(self.assignee_email,self.assigneeSubject,self.assigneeBody)

        elif self.IssueCommented :
            if self.includeCreator :
                mail(self.creator_email,self.creatorSubject,self.creatorBody)
            mail(self.assignee_email,self.assigneeSubject,self.assigneeBody)
            mail(self.commentor_email,self.commentorSubject,self.commentorBody)

        elif self.IssueAssigned :
            if self.includeCreator :
                mail(self.creator_email,self.creatorSubject,self.creatorBody)
            mail(self.assignee_email,self.assigneeSubject,self.assigneeBody)
            mail(self.assigner_email,self.assignerSubject,self.assignerBody)
            mail(self.new_assignee_email,self.newAssgineeSubject,self.newAssigneeBody)

        elif self.IssueWorkStarted :
            if self.includeCreator :
                mail(self.creator_email,self.creatorSubject,self.creatorBody)
            mail(self.assignee_email,self.assigneeSubject,self.assigneeBody)
            mail(self.starter_email,self.starterSubject,self.starterBody)

        elif self.IssueWorkStopped :
            if self.includeCreator :
                mail(self.creator_email,self.creatorSubject,self.creatorBody)
            mail(self.assignee_email,self.assigneeSubject,self.assigneeBody)
            mail(self.stopper_email,self.stopperSubject,self.stopperBody)

        elif self.IssueResolved :
            if self.includeCreator :
                mail(self.creator_email,self.creatorSubject,self.creatorBody)
            mail(self.assignee_email,self.assigneeSubject,self.assigneeBody)
            mail(self.resolver_email,self.resolverSubject,self.resolverBody)

        elif self.IssueClosed :
            if self.includeCreator :
                mail(self.creator_email,self.creatorSubject,self.creatorBody)
            mail(self.assignee_email,self.assigneeSubject,self.assigneeBody)
            mail(self.closer_email,self.closerSubject,self.closerBody)

        else :
            raise ValueError        

    # METHOD FOR REPRESENTING THE CLASS

    def __repr__(self):
        return self.issue_type
