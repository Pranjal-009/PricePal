function toggleCompare(button) {
    const card = button.parentElement;
    const prices = card.querySelectorAll('.platform-price, .price');
    let isHidden = prices[0].style.display === 'none' || prices[0].style.display === '';

    prices.forEach(price => {
        price.style.display = isHidden ? 'block' : 'none';
    });

    if (isHidden) {
        button.textContent = 'Hide Prices';
        button.classList.add('hide-mode');
    } else {
        button.textContent = 'Compare Prices';
        button.classList.remove('hide-mode');
    }
}
