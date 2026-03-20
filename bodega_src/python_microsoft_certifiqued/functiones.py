# Add your code here
def make_sandwich(bread_type, filling, cheese = None, toasted = False):
    """
    Creates a sandwich with optional ingredents.

    Args:
        bread_type (str): the type of bread (required).
        filling (str):  the main sandwich filling (required).
        cheese (str, optional): the cheese type (defaults to None).
        toasted (bool, optional):  indicating if the sandwich is toasted (defaults to False).

    Returns:
        main_recet (str): full sandwich string content.
    """      

    toasted_state = ""

    if toasted:
        toasted_state = " toasted"

    if cheese is not None:
        cheese = f" and {cheese} cheese"
    else:
        cheese = ""


    main_recet = f"Making a{toasted_state} {bread_type} sandwich with {filling}{cheese}."
    return main_recet





#---------------------------------------------------------------
# Add the SKU data provided to the product catalog dictionary
product_catalog = {
    "SKU123": {
        "name": "Widget A",
        "price": 19.99,
        "quantity": 50
    },
    "SKU456": {
	    "name": "Gadget B",
	    "price": 34.95,
	    "quantity": 25
	},
	"SKU789": {	    
	    "name": "Gizmo C",
	    "price": 9.99,
	    "quantity": 100 		
	}
} 
# Look up this SKU in your code. 
sku_to_find = "SKU123"
price = product_catalog[sku_to_find]["price"]
print(f"The price of {product_catalog[sku_to_find]['name']} is ${price}")
