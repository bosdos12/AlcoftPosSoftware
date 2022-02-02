# The Restaurant billing system will be the best in the local standard

# Features I need:
  1. Login screen;
  2. Standby screen;
  3. Table's screen;
  4. Billing having its individual screen;
  5. The same payment logic as the tkinter app I built;
  6. The bill info's will be stored on the selling computer;
  7. Each sale will create a bill-file on the computer, the saved bill files will be in some data-access format;
  8. Each day there will also be a daily totals file, where each products will be stacked on each other, the prices added, the total will show; Also weekly and monthly totals;
  9. There will also be a statistics page, the shop/employee/employer/yougetthepoint will be able to search for days/dates and see which products were sold how much;
  10. On the go mobile system - A waiter will be able to just walk up to people, ask for an order, send this to the server and server will send it to the restaurants pc;
  11. The waiter will also be able to finish transactions from the phone via table-id's;
  12. Both the mobile and desktop system will be able to
  13. Logo/Image path settings;
  14. Settings screen;

  # Preference based usage stuff:
    1. Whenever a new sale gets accepted on the cashier-side, a request gets sent to the chef pc with the data, the chef can either accept or reject the request,
       The request contains all the ordered stuff, if the chef accepts it the table gets filled and everything goes on normaly, otherwise nothing happens, the chef just waits for other orders;

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
How is the system gonna work on mobile while staying synchronous with the desktop in the restaurant:
  The desktops\restaurants prices/products will be up running on the server;
  Each table will also have its own server spot with its own table-id;
  Whenever products get added to a certain table, the products will be temporarily on the phone, to allow DELETION and PRODUCT-HAS-BEEN-SENT etc;
  Active orders will always stay on the server;
  
  The mobile will go to tables it wants, the table count will be done via the server count access;
  The mobile will allow closed tables to be opened, active bills being transaction-done, deletion of ordered items, *sent* stating of the ordered items;
