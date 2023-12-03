from telethon.sync import TelegramClient, events
from yowsup.env import YowsupEnv
from yowsup.stacks import YowStackBuilder
from yowsup.layers import YowParallelLayer
from yowsup.layers.auth import YowAuthenticationProtocolLayer
from yowsup.layers.protocol_messages import YowMessagesProtocolLayer
from yowsup.layers.protocol_receipts import YowReceiptProtocolLayer
from yowsup.layers.protocol_acks import YowAckProtocolLayer
from yowsup.layers.network import YowNetworkLayer
from yowsup.common import YowConstants

# Telegram API credentials
telegram_api_id = 'YOUR_TELEGRAM_API_ID'
telegram_api_hash = 'YOUR_TELEGRAM_API_HASH'
telegram_phone = 'YOUR_PHONE_NUMBER'

# WhatsApp API credentials
whatsapp_phone = "YOUR_PHONE_NUMBER_WITH_COUNTRY_CODE"
whatsapp_password = "YOUR_WHATSAPP_PASSWORD"

# WhatsApp group ID (replace with your group ID)
whatsapp_group_id = "GROUP_ID@chat.whatsapp.net"

# Initialize Telegram client
telegram_client = TelegramClient('session_name', telegram_api_id, telegram_api_hash)

# Initialize WhatsApp connection
whatsapp_stackBuilder = YowStackBuilder()
whatsapp_stack = whatsapp_stackBuilder \
    .pushDefaultLayers(True) \
    .push(YowParallelLayer([YowAuthenticationProtocolLayer, YowMessagesProtocolLayer, YowReceiptProtocolLayer, YowAckProtocolLayer])) \
    .build()
whatsapp_stack.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS, (whatsapp_phone, whatsapp_password))
whatsapp_stack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])
whatsapp_stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))

# Telegram event NewMessage
@telegram_client.on(events.NewMessage)
async def handle_new_message(event):
    # Forward Telegram message content to WhatsApp group
    await forward_to_whatsapp(event.message.message)

# Forward message to WhatsApp
async def forward_to_whatsapp(content):
    if whatsapp_stack.isConnected():
        whatsapp_stack.sendLayerMessage(YowMessagesProtocolLayer.toLower(TextMessageProtocolEntity(content, to=whatsapp_group_id)))

# Start Telegram client
telegram_client.start(telegram_phone)

# Start event loop
telegram_client.run_until_disconnected()
