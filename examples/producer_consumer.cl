// Producer-Consumer Example
// This demonstrates channel communication between parallel threads

chan<int> buffer;
int count = 0;
int value = 0;

parallel {
  // Producer thread
  send(buffer, 1);
  send(buffer, 2);
  send(buffer, 3);
}

parallel {
  // Consumer thread
  value = recv(buffer);
  value = recv(buffer);
  value = recv(buffer);
}
