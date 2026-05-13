const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const MediaProvenance = await hre.ethers.getContractFactory("MediaProvenance");
  const contract = await MediaProvenance.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  const network = await hre.ethers.provider.getNetwork();

  console.log("MediaProvenance deployed");
  console.log(`network=${hre.network.name}`);
  console.log(`chainId=${network.chainId.toString()}`);
  console.log(`deployer=${deployer.address}`);
  console.log(`contract=${address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
