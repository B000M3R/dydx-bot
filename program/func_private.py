from datetime import datetime, timedelta
from func_utils import format_number
import time
from pprint import pprint

# Place market order
def place_market_order(client, market, side, size, price, reduce_only):
    from datetime import datetime, timedelta
    import pytz

    # Get Position ID
    account_response = client.private.get_account()
    position_id = account_response.data["account"]["positionId"]

    # Get expiration Time
    server_time = client.public.get_time()

    # Manually fix the ISO string format
    iso_str = server_time.data["iso"]

    # Split the string on the 'T' to separate date and time
    date_part, time_part = iso_str.split('T')

    # Further split the time on ":" to get hours, minutes, and seconds
    hours, minutes, seconds = time_part.split(':')

    # If seconds are single digit, prefix with "0"
    if len(seconds.split('.')[0]) == 1:
        seconds = '0' + seconds

    # Reassemble the string without the 'Z' character
    fixed_iso_str = date_part + 'T' + hours + ':' + minutes + ':' + seconds[:-1]

    # Calculate expiration time
    expiration = datetime.fromisoformat(fixed_iso_str).replace(tzinfo=pytz.UTC) + timedelta(seconds=70)

    # Place an Order
    placed_order = client.private.create_order(
        position_id=position_id,
        market=market,
        side=side,
        order_type="MARKET",
        post_only=False,
        size=size,
        price=price,
        limit_fee='0.015',
        expiration_epoch_seconds=expiration.timestamp(),
        time_in_force="FOK",
        reduce_only=reduce_only
    )

    # Return result
    return placed_order.data

# Abort all open positions
def abort_all_positions(client):
    # Cancel all order
    client.private.cancel_all_orders()

    # Protect API
    time.sleep(0.5)

    # Get markets for reference of tick size
    markets = client.public.get_markets().data

    # Protect API
    time.sleep(0.5)


    # Get ALL Open Positions
    positions = client.private.get_positions(status="OPEN")
    all_positions = positions.data["positions"]

    pprint(all_positions)

    # Handle open positions
    close_orders = []
    if len(all_positions) > 0:
        # Loop through each position
        for position in all_positions:
            # Determine Market
            market = position["market"]

            # Determine Side
            side = "BUY"
            if position["side"] == "LONG":
                side = "SELL"

            # Get Price
            price = float(position["entryPrice"])
            accept_price = price * 1.7 if side == "BUY" else price * 0.3
            tick_size = markets["markets"][market]["tickSize"]
            accept_price = format_number(accept_price, tick_size)

            # Place order to close
            order = place_market_order(
                client,
                market,
                side,
                position["sumOpen"],  # Added missing comma here
                accept_price,
                True
            )

            # Append the result
            close_orders.append(order)

            # Protect API
            time.sleep(0.2)

        # Return closed orders
        return close_orders
