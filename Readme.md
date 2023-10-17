
## Running the Code

To run the code, you will need to provide the paths to the following files:

### Data

* The path to the TA CSV file:
     ``TA_csv: "TA.csv"``
* The path to the courses CSV file:
     ``courses_csv: "courses.csv"``

Once you have provided these paths, you can run the code as follows:
 ```sh
      python3 .\Ta_allocation.py --TA_csv 'TA.csv' --course_csv 'courses.csv'
   ``` 
This will run the inference stage and save the submission file to the current directory.
