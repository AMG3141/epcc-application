# Import relevant libraries
library(TDA)
library(ggplot2)
library(igraph)

# Import the (adjusted) closing prices for all companies for which we have data
# dataDir - the directory containing the companies' data files
# dataCol - the column we want to extract
# outputFile - the filename to give the output csv
importData = function(dataDir, dataCol, outputFile) {
	oldDir = getwd()

	# Import all the data
	dateRanges = data.frame("Company" = character(), "Start" = integer(), "End" = integer())

	setwd(dataDir)
	i = 0
	for (path in dir()) {
		i = i + 1

		# Find the earliest and latest dates we have for each company
		companyName = substr(path, 1, nchar(path) - 4)
		f = read.csv(path)
		earlyDate = as.integer(as.Date(head(f$Date, n=1)))
		lateDate = as.integer(as.Date(tail(f$Date, n=1)))

		dateRanges[i,] = list(companyName, earlyDate, lateDate)
	}

	# Get the (adjusted) closing price data for each company
	priceData = data.frame("Date" = min(dateRanges$Start):max(dateRanges$End))

	for (path in dir()) {
		f = read.csv(path)
		companyName = substr(path, 1, nchar(path) - 4)
		relevantData = data.frame("Date" = as.integer(as.Date(f$Date)), dataCol = as.numeric(f[[dataCol]]))
		names(relevantData)[2] = dataCol # <.\_/.>

		# Remove days for which we have no information
		badRows = which(is.na(relevantData[[dataCol]]), relevantData[[dataCol]])
		if (length(badRows) != 0)
			relevantData = relevantData[-badRows, ]

		# Add all days for which we have information to the data frame (either NA or NULL for days when we don't)
		priceData[[companyName]] = relevantData[[dataCol]][match(priceData[["Date"]], relevantData$Date)]

		# Remove days for which we have no information at all
		v = rowSums(is.na(priceData)) != ncol(priceData) - 1
		priceData = priceData[v, ]

		############################################################
		# This will give us the earliest date for which we have all companies (i.e. 0 NA's in the frame)
		# as.Date(priceData[rowSums(is.na(priceData)) == 0,]$Date[1])
		############################################################
	}

	setwd(oldDir)

	# readableDateRanges = data.frame("Company" = dateRanges$Company, "Start" = as.Date(dateRanges$Start), "End" = as.Date(dateRanges$End))

	write.csv(priceData, outputFile, row.names = F)
}

# Calculate the distance according to the formula between stocks c1 and c2
# c1 - name of stock 1
# c2 - name of stock 2
# t - the date to use
# horizonT - the size of the time horizon (in days)
# priceData - a data frame with the (adjusted) closing prices for a series of dates
distance = function(c1, c2, t, horizonT, priceData) {
	# Import data if necessary
	if (class(priceData) == "character") priceData = read.csv(priceData, check.names = F)

	# Convert t if necessary
	if (!asTimeStamp) t = unclass(as.Date(t))

	# Get rows from data which correspond to the given time horizon
	tRow = which(priceData$Date == t)
	horizonRows = priceData[(tRow - horizonT + 1):tRow,]

	# Get the adjusted closing prices for the companies we care about
	c1Adj.close = horizonRows[[c1]]
	c2Adj.close = horizonRows[[c2]]

	# Calculate the distance between these two companies over the given time horizon
	return(sqrt(2 * (1 - cor(c1Adj.close, c2Adj.close))))
}

# Calculate the weighted network for a given time horizon, return the latest value of t is could use with the associated adjacency matrix
# t - the last date to use (if this date cannot be found, will use the latest possible date before this)
# horizonT - the size of the time horizon (in days)
# priceData - a data frame with the (adjusted) closing prices for a series of dates
# removeNA - boolean value to indicate if the rows and columns which are entirely NA (apart from diagonal) should be removed (TRUE by default)
# subLevel - boolean value to indicate a sub-/super-level set (TRUE by default)
calcNetwork = function(t, horizonT, priceData, removeNA = T, subLevel = T) {
	# Import data if necessary
	if (class(priceData) == "character") priceData = read.csv(priceData, check.names = F)

	# Convert t if necessary
	if (class(t) == "character") t = unclass(as.Date(t))

	# Work backwards to find a valid value of t (if the supplied one isn't valid)
	while (length(which(priceData$Date == t)) == 0) t = t - 1

	# Get company names and set up matrix
	companyNames = colnames(priceData)[-1]
	netMat = matrix(double((ncol(priceData) - 1)^ 2), nrow = ncol(priceData) - 1)

	# Calculate the distance between each pair of stocks for the given time horizon
	for (i in 1:(length(companyNames) - 1)) {
		for (j in (i + 1):length(companyNames)) {
			val = distance(companyNames[i], companyNames[j], t, horizonT, priceData)
			netMat[i, j] = if (subLevel) val else 2 - val
		}
	}

	# Convert the upper triangular matrix to a symmetric matrix by adding it to its transpose (don't need to worry about diagonal, will always be 2)
	netMat = netMat + t(netMat)

	# Set diagonal elements to 2
	for (i in 1:ncol(netMat)) netMat[i, i] = 2

	# Remove any NA's (only a problem if there are dates for which one or more companies aren't on the index)
	if (length(which(rowSums(is.na(netMat)) == nrow(netMat))) != 0 & removeNA)
			netMat = netMat[-which(rowSums(is.na(netMat)) == nrow(netMat) - 1), -which(colSums(is.na(netMat)) == ncol(netMat) - 1)]

	return(list(t, netMat))
}

# Makes the plot of distances of persistence diagrams
# startDate - the date to start from (if as a string has format "YYYY-MM-DD")
# endDate - the date to end at (if as a string has format "YYYY-MM-DD")
# horizonT - the size of the time horizon (in days)
# timeStep - the size of the step to take for each iteration (in days)
# priceData - either a data frame with the (adjusted) closing prices for a series of dates or the path to such a frame in csv form
# subLevel - boolean value to indicate a sub-/super-level set
# dimension - the dimension to use when calculating the Wasserstein distances
generatePlot = function(startDate, endDate, horizonT, timeStep, priceData, subLevel, dimension) {
	# Import data if necessary
	if (class(priceData) == "character") priceData = read.csv(priceData, check.names = F)

	# Set up range of dates we are interested in
	if (class(startDate) == "character") startDate = as.Date(startDate)
	if (class(endDate) == "character") endDate = as.Date(endDate)

	actualTimesList = list()
	complexList = list()

	for (t in seq(startDate, endDate, timeStep)) {
		# Calculate full, weighted network for each given time
		# Network represented as a square matrix (any companies for which there is no data will be removed)
		calcNetworkOutput = calcNetwork(t, horizonT, priceData, removeNA = T, subLevel = subLevel)
		actualTimesList[[t]] = calcNetworkOutput[[1]]
		netMat = calcNetworkOutput[[2]]

		# Calculate the Rips complex for the network at this time (can easily get diagram/barcode)
		complexList[[t]] = ripsDiag(netMat, maxdimension = 1, maxscale = 2, dist = "arbitrary", printProgress = F)
	}

	# Remove all the null entries (they come about due to the fact that I am creating list entries e.g. 14123, 14124, etc. and it fills the first however many blank entries with null)
	actualTimesList = actualTimesList[-which(lapply(actualTimesList, is.null) == T)]
	complexList = complexList[-which(lapply(complexList, is.null) == T)]

	# For all the generated complexes, measure the distance (using the Wasserstein distance) of the barcode/persistence diagram from the initial complex
	distances = list()
	referenceDiag = complexList[[1]][["diagram"]]

	for (i in 1:length(complexList)) {
		# plot(complexList[[i]][["diagram"]], barcode = T)
		distances[[i]] = wasserstein(referenceDiag, complexList[[i]][["diagram"]], p = 2, dimension = dimension)
	}

	# Configure data for plotting
	actualDatesObj = as.Date(unlist(lapply(actualTimesList, as.Date)))

	# Plot the distances from the first diagram
	plotTitle = if (subLevel) "Sub-Level" else "Super-Level"
	plotTitle = paste(plotTitle, " Dimension ", dimension)
	pFull = ggplot(data = data.frame(Date = actualDatesObj, Distance = unlist(distances)), aes(x = Date, y = Distance)) + geom_line() + ggtitle(plotTitle) + geom_vline(xintercept = unclass(as.Date("2016-06-23")), linetype = "dashed", color = "red")

	# Restrict the data to before the referendum
	refDay = unclass(as.Date("2016-06-23"))
	validDaysIndices = which(actualTimesList < refDay)
	validDays = actualTimesList[validDaysIndices]
	validDaysObj = as.Date(unlist(lapply(validDays, as.Date)))
	validDists = distances[validDaysIndices]

	pBefore = ggplot(data = data.frame(Date = validDaysObj, Distance = unlist(validDists)), aes(x = Date, y = Distance)) + geom_line() + ggtitle(paste(plotTitle, " Before Referendum"))

	# Restrict the data to after the referendum
	validDaysIndices = which(actualTimesList > refDay)
	validDays = actualTimesList[validDaysIndices]
	validDaysObj = as.Date(unlist(lapply(validDays, as.Date)))
	validDists = distances[validDaysIndices]

	pAfter = ggplot(data = data.frame(Date = validDaysObj, Distance = unlist(validDists)), aes(x = Date, y = Distance)) + geom_line() + ggtitle(paste(plotTitle, " After Referendum"))

	return(list("ActualTimes" = unlist(actualTimesList), "ActualDates" = actualDatesObj, "Diagrams" = complexList, "Distances" = unlist(distances), "FullPlot" = pFull, "PreRefPlot" = pBefore, "PostRefPlot" = pAfter))
}

################################################################################

# Get all the plots
startDate = "2015-01-01"
endDate = "2017-12-29"
horizonT = 15
timeStep = 1
priceData = "djiaPrices.csv"

subLevel0 = generatePlot(startDate, endDate, horizonT, timeStep, priceData, T, 0)
subLevel1 = generatePlot(startDate, endDate, horizonT, timeStep, priceData, T, 1)
superLevel0 = generatePlot(startDate, endDate, horizonT, timeStep, priceData, F, 0) # Big spike is 2015-08-28. Don't know what is happening there......
superLevel1 = generatePlot(startDate, endDate, horizonT, timeStep, priceData, F, 1)

################################################################################

# Show some possibly interesting information on the plots
for (li in list(subLevel0, subLevel1, superLevel0, superLevel1)) {
	li$FullPlot$labels$title = NULL
	li$PreRefPlot$labels$title = NULL
	li$PostRefPlot$labels$title = NULL

	print(li$FullPlot + geom_vline(xintercept = unclass(as.Date("2016-06-23")), linetype = "dashed", color = "red")) # Day of referendum

	print(li$PreRefPlot + geom_vline(xintercept = unclass(as.Date("2016-02-20")), linetype = "dashed", color = "green") + # Referendum announced
						  geom_vline(xintercept = unclass(as.Date("2016-04-15")), linetype = "dashed", color = "blue") +  # EU referendum campaign officially begins
						  geom_vline(xintercept = unclass(as.Date("2016-06-14")), linetype = "dashed", color = "orange"))  # Poll showing leave more likely (FTSE100 lost 98 billion)

		print(li$PostRefPlot)
}

################################################################################

# Show some example graphs far from the referendum and close to the referendum
igraph.options(plot.layout=layout.circle)

theta = 1.5
netMatFar1Output = calcNetwork("2015-01-02", horizonT, priceData)
netMatFar1t = netMatFar1Output[[1]]
netMatFar1 = netMatFar1Output[[2]]
netMatFar1[which(netMatFar1 < theta)] = 0
plot(graph_from_adjacency_matrix(netMatFar1, "undirected", T, F))

netMatFar2Output = calcNetwork("2015-12-31", horizonT, priceData)
netMatFar2t = netMatFar2Output[[1]]
netMatFar2 = netMatFar2Output[[2]]
netMatFar2[which(netMatFar2 < theta)] = 0
plot(graph_from_adjacency_matrix(netMatFar2, "undirected", T, F))

netMatClose1Output = calcNetwork("2016-05-23", horizonT, priceData)
netMatClose1t = netMatClose1Output[[1]]
netMatClose1 = netMatClose1Output[[2]]
netMatClose1[which(netMatClose1 < theta)] = 0
plot(graph_from_adjacency_matrix(netMatClose1, "undirected", T, F))

netMatClose2Output = calcNetwork("2016-06-22", horizonT, priceData)
netMatClose2t = netMatClose2Output[[1]]
netMatClose2 = netMatClose2Output[[2]]
netMatClose2[which(netMatClose2 < theta)] = 0
plot(graph_from_adjacency_matrix(netMatClose2, "undirected", T, F))

################################################################################

# Show some example presistence barcodes far from the referendum and close to the referendum
plot(subLevel0$Diagrams[[which(subLevel0$ActualDates == "2015-01-02")[1]]][["diagram"]], barcode = T)
plot(subLevel0$Diagrams[[which(subLevel0$ActualDates == "2015-12-31")[1]]][["diagram"]], barcode = T)
plot(subLevel0$Diagrams[[which(subLevel0$ActualDates == "2016-05-23")[1]]][["diagram"]], barcode = T)
plot(subLevel0$Diagrams[[which(subLevel0$ActualDates == "2016-06-22")[1]]][["diagram"]], barcode = T)