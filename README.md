# IgScrapper
<p>
An Instagram scrapper, intended to generate trainingdata for downstream Machine Learning and Deep Learning applications. 
<p>    
Downloads jpgs as well as metadata of this post.
<p>    
Input: UserList.txt: a text file with usernames of Instagram profiles.
    e.g. for the profile : https://www.instagram.com/sony/?hl=en, the username would be /sony/  
    format of textfile:   
    /username1/  
    /username2/  
    /username3/  
    ...  
 <p>    
 Output:
     1. An SQlite database containing the metadata of all scrapped images
        Metadata: *"photo_name" unique identifier, 
                  *"photo_url" url of post, 
                  *"likes" number of likes, 
                  *"age" age of post in days, 
                  *"downloaded" date when post was downloaded, 
                  *"IG_category" some posts are classified by instagram, in this case, they are saved, 
                  *"hashtags" all hashtags of post, 
                  *"photographer_name" Instagram username, 
                  *"followers" number of followers of Instagram user, 
                  *"following" number of users that this Instagram user is following, 
                  *"manually_confirmed" auxillary collumn to be used to manually clean the dataset, 
                  *"is_downloaded" "True", if jpg has been saved, "False" if post still needs to be scrapped
     2. jpgs of the users in UserList.txt. They will be placed in folders named by : username
 <p>    
 Requirements:
      instaloader
      selenium 
      sqlite3
      time
      random
      datetime
      os
  


 
