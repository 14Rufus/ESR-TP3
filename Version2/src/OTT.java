import java.io.IOException;
import java.net.*;

public class OTT {


    public static void main(String[] args) throws IOException, InterruptedException {

        // IP address and port of HttpGw
//        InetAddress address = InetAddress.getByName(args[0]);
//        int port = Integer.parseInt(args[1]); // porta à qual se pretende ligar

        // Recebe informação
        ServerSocket serverSocket = new ServerSocket(8081);
        // X client sockets para enviar informação
        Socket clientSocket = new Socket("127.0.0.1",8081);

        Thread s = new Thread(new OTTServerWorker(serverSocket,clientSocket));
        Thread c = new Thread(new OTTClientWorker(clientSocket));


        s.start();
        c.start();

        s.join();
        c.join();
    }
}
