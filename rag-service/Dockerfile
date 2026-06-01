FROM golang:alpine

WORKDIR /app

# Install git since some go modules need it
RUN apk add --no-cache git

COPY go.mod ./
COPY main.go ./

# Tidy will fetch the dependencies
RUN go mod tidy

# Build the application
RUN go build -o main .

# Expose port
EXPOSE 8080

CMD ["./main"]
