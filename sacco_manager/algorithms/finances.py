from sacco_manager.models import FareTransactions


class FinancesSavingOperations:
    def saveFareTransactions(self,vehicle,traveller,amount,departure,destination):
        if FareTransactions.objects.create(vehicle=vehicle,traveller=traveller,amount=amount,departure_town=departure,destination_town=destination):
            return True
        else:
            return False

