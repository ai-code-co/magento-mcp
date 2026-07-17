<?php
/**
 * Fix local Magento integration permissions for MCP.
 * Run: php C:\Users\Etech\Desktop\magento-mcp\fix_integration.php
 */
use Magento\Framework\App\Bootstrap;
use Magento\Integration\Api\AuthorizationServiceInterface;
use Magento\Integration\Model\ResourceModel\Oauth\Token as TokenResource;
use Magento\Integration\Model\Oauth\TokenFactory;

require 'C:/xampp/htdocs/magento3/app/bootstrap.php';

$bootstrap = Bootstrap::create(BP, $_SERVER);
$om = $bootstrap->getObjectManager();

$state = $om->get(\Magento\Framework\App\State::class);
try {
    $state->setAreaCode('adminhtml');
} catch (\Exception $e) {
    // area already set
}

$integrationId = 1;
/** @var AuthorizationServiceInterface $auth */
$auth = $om->get(AuthorizationServiceInterface::class);
$auth->grantAllPermissions($integrationId);
echo "Granted ALL API permissions to integration_id={$integrationId}\n";

/** @var TokenFactory $tokenFactory */
$tokenFactory = $om->get(TokenFactory::class);
$token = $tokenFactory->create()->loadByConsumerIdAndUserType(
    1,
    \Magento\Authorization\Model\UserContextInterface::USER_TYPE_INTEGRATION
);

if (!$token->getId()) {
    fwrite(STDERR, "No access token found for consumer_id=1\n");
    exit(1);
}

if (!(int)$token->getAuthorized()) {
    $token->setAuthorized(1)->save();
    echo "Marked access token as authorized\n";
}

$accessToken = $token->getToken();
$envPath = __DIR__ . '/.env';
$env = file_exists($envPath) ? file_get_contents($envPath) : '';
if (preg_match('/^ACCESS_TOKEN=.*$/m', $env)) {
    $env = preg_replace('/^ACCESS_TOKEN=.*$/m', 'ACCESS_TOKEN=' . $accessToken, $env);
} else {
    $env .= "\nACCESS_TOKEN=" . $accessToken . "\n";
}
if (!preg_match('/^MAGENTO_URL=/m', $env)) {
    $env = "MAGENTO_URL=http://magento3.local/rest/V1\n" . $env;
} else {
    $env = preg_replace(
        '/^MAGENTO_URL=.*$/m',
        'MAGENTO_URL=http://magento3.local/rest/V1',
        $env
    );
}
file_put_contents($envPath, $env);

echo "Updated .env ACCESS_TOKEN from Magento (token length=" . strlen($accessToken) . ")\n";
echo "Done. Test with: python app.py products --limit 5\n";
