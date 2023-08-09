def main():
    mac_address = 'FF:FF:FF:FF:FF:FF'

    mac = mac_address.split(':')
    print(all(x == 'FF' for x in mac))


if __name__ == '__main__':
    main()
