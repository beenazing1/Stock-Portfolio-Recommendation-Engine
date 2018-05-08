# Stock-Portfolio-Recommendation-Engine
A portfolio recommendation engine based on user inputs which have an objective of minimizing risk given the approximate tolerance on the return




# DESCRIPTION 

Portfolio Recommendation Engine: To help naive investors make better decisions by 
suggesting an optimal portfolio based on user inputs which have an objective of minimizing risk given 
the approximate tolerance on the return.



# INSTALLATION
(also refer to the description file in the CODE folder to know more about the backend models used)


 - Python 2.7 is needed for the demo to run
 - Please install the required Dependencies:
		- Download the Flask library in order to use our application. 

           pip install Flask
		   
		- Download the required packages in python :

           pip install pandas numpy datetime
		   
		- Download the Gurobi optimization software. 
			 - You must register at www.gurobi.com from a Georgia Tech IP address to obtain a license.
			 - Then download and install from http://www.gurobi.com/downloads/gurobi-optimizer. 
			 - Documentation available at https://www.gurobi.com/documentation
			 - From an Anaconda terminal issue the following command to add the Gurobi channel to your default search list:
			 
				conda config --add channels http://conda.anaconda.org/gurobi

			 - Now issue the following command to install the Gurobi package

				conda install gurobi

			 - License requirement for Gurobi
				 - After registering through Georgia Tech's IP address - please visit page
				https://user.gurobi.com/download/licenses/free-academic and click on 
				Request License
				 - Once directed to the new page follow instructions and copy paste the
				 grbgetkey command to run menu. 



		
# EXECUTION

- Download the UI file in the CODE folder
- Run the app.py file then go to the displayed URL

		  python app.py

- Follow the UI steps to get your optimal stock portfolio allocation






