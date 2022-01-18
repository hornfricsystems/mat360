class ProcessSaccoFinances:
    """
    This is the method that will incorporate all payments away from MPESA.
    """
    def withDrawFromMat360WorkingAccount(self,workingAccount,UtilityAccount):
        '''This is the method that will sacco use to withdraw their money from our account to their account
        It uses the safaricom B2B for paybills.'''