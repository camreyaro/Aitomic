from aitomic.paypal.paypalsdk import PayPalClient
from paypalcheckoutsdk.orders import OrdersGetRequest
from aitomic.models import Payment, ModelBought, AIModel
from django.utils import timezone
import datetime


class GetOrder(PayPalClient):
    # Set up the server to receive a call from the client

    """You can use this function to retrieve an order by passing order ID as an argument"""
    def get_order(self, order_id, model_id, user, quantity, moment_to_use):
        """Method to get order"""
        request = OrdersGetRequest(order_id)
        # 3. Call PayPal to get the transaction
        response = self.client.execute(request)
        # 4. Save the transaction in your database. Implement logic to save transaction to your database for
        # future reference.
        #print('Status Code: ', response.status_code)
        #print('Status: ', response.result.status)
        #print('Order ID: ', response.result.id)
        #print('Intent: ', response.result.intent)
        #print('Links:')
        #for link in response.result.links:
        #    print('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method))
        #print('Gross Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code,
        #                             response.result.purchase_units[0].amount.value))

        # Saving Payment and ModelBought
        if response.result.status == 'COMPLETED' and response.status_code == 200:
            price = response.result.purchase_units[0].amount.value
            model = AIModel.objects.get(pk=model_id)
            moment_to_use = str(moment_to_use)
            moment_to_use = datetime.datetime.strptime(moment_to_use, "%Y%m%d").date()
            payment = Payment.objects.create(orderID=order_id, quantity=quantity, price=price, user=user, model=model)

            #models_bought = ModelBought.objects.filter(user=user, model=model)

            # if models_bought.exists():  # Checks if the user has already bought the model and has calls left
            #     model_bought = models_bought.first()
            #
            #     model_bought.moment = timezone.now()
            #     model_bought.totalCalls = model_bought.totalCalls + int(quantity)
            #     model_bought.callsLeft = model_bought.callsLeft + int(quantity)
            #
            # else:
            model_bought = ModelBought.objects.create(user=user, model=model, totalCalls=int(quantity),
                                                          callsLeft=int(quantity), moment_to_use=moment_to_use)

            payment.save()
            model_bought.save()


    """This is the driver function that invokes the get_order function with
       order ID to retrieve sample order details. """
if __name__ == '__main__':
    GetOrder().get_order('REPLACE-WITH-VALID-ORDER-ID')