from locust import HttpUser, between, task


class CatsAndDogsUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def home(self):
        self.client.get("/", name="/")

    @task
    def cats(self):
        self.client.get("/cats", name="/cats")

    @task
    def dogs(self):
        self.client.get("/dogs", name="/dogs")